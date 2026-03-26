package com.example.aikeyboard.keyboard

import android.app.Activity
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Color
import android.graphics.PixelFormat
import android.hardware.display.DisplayManager
import android.inputmethodservice.InputMethodService
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.util.DisplayMetrics
import android.view.KeyEvent
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.view.WindowManager
import android.view.inputmethod.InputMethodManager
import android.widget.*
import androidx.core.view.isGone
import androidx.core.view.isVisible
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.aikeyboard.R
import com.example.aikeyboard.data.local.EncryptedPrefsManager
import com.example.aikeyboard.data.remote.*
import com.example.aikeyboard.service.ScreenshotService
import com.example.aikeyboard.utils.AiPrompts
import com.example.aikeyboard.utils.AppConfig
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.*
import okhttp3.Interceptor
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import kotlin.math.max

class AIKeyboardService : InputMethodService(), ClipboardManager.OnPrimaryClipChangedListener {

    private lateinit var viewFlipper: ViewFlipper
    private lateinit var aiHeader: FrameLayout
    private lateinit var tvAiReply: TextView
    private lateinit var loadingProgress: ProgressBar
    private lateinit var btnGenerate: Button
    private lateinit var tvDocsList: TextView
    private lateinit var tvServerStatus: TextView
    private lateinit var viewServerStatus: View
    private lateinit var btnCaptureScreenshot: Button
    private lateinit var btnRetryOcr: Button
    private lateinit var ivScreenshotPreview: ImageView
    private lateinit var llScreenshotStatus: LinearLayout
    private lateinit var tvScreenshotStatus: TextView
    private lateinit var tvExtractedText: TextView
    private lateinit var toolsLoader: ProgressBar
    
    // Spam UI
    private lateinit var layoutSpam: LinearLayout
    private lateinit var etSpamText: EditText
    private lateinit var etSpamCount: EditText
    private lateinit var etSpamInterval: EditText
    private lateinit var btnStartSpam: Button
    private lateinit var btnCancelSpam: Button
    private var spamJob: Job? = null

    // QWERTY UI State
    private var isShifted = false
    
    private lateinit var prefsManager: EncryptedPrefsManager
    private val serviceScope = CoroutineScope(SupervisorJob() + Dispatchers.Main)
    private var statusJob: Job? = null
    private var lastCapturedBitmap: Bitmap? = null
    private var currentMediaProjection: MediaProjection? = null

    private val historyList = mutableListOf<HistoryItem>()
    private lateinit var historyAdapter: HistoryAdapter

    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

    private val commonWords = listOf("the", "to", "and", "a", "of", "in", "is", "it", "you", "that", "he", "was", "for", "on", "are", "with", "as", "I", "his", "they", "be", "at", "one", "have", "this", "from", "or", "had", "by", "hot", "word", "but", "what", "some", "we", "can", "out", "other", "were", "all", "there", "when", "up", "use", "your", "how", "said", "an", "each", "she")

    private val apiService: ApiService get() = createApiService()

    private fun createApiService(): ApiService {
        val userTimeout = AppConfig.getTimeoutSeconds(this)
        val timeoutInSeconds = max(300L, if (userTimeout > 1000) userTimeout / 1000 else userTimeout)
        
        val okHttpClient = OkHttpClient.Builder()
            .connectTimeout(timeoutInSeconds, TimeUnit.SECONDS)
            .readTimeout(timeoutInSeconds, TimeUnit.SECONDS)
            .writeTimeout(timeoutInSeconds, TimeUnit.SECONDS)
            .addInterceptor(Interceptor { chain ->
                val original = chain.request()
                val token = prefsManager.getAccessToken()
                val request = if (token != null) {
                    original.newBuilder()
                        .header("Authorization", "Bearer $token")
                        .build()
                } else {
                    original
                }
                chain.proceed(request)
            })
            .build()

        return Retrofit.Builder()
            .baseUrl(AppConfig.getBaseUrl(this))
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }

    override fun onCreate() {
        super.onCreate()
        prefsManager = EncryptedPrefsManager(this)
        val clipboard = getSystemService(ClipboardManager::class.java)
        clipboard?.addPrimaryClipChangedListener(this)
        startStatusUpdates()
    }

    override fun onDestroy() {
        super.onDestroy()
        val clipboard = getSystemService(ClipboardManager::class.java)
        clipboard?.removePrimaryClipChangedListener(this)
        serviceScope.cancel()
        currentMediaProjection?.stop()
        spamJob?.cancel()
    }

    override fun onCreateInputView(): View {
        val view = LayoutInflater.from(this).inflate(R.layout.keyboard_view, null)

        viewFlipper = view.findViewById(R.id.viewFlipper)
        aiHeader = view.findViewById(R.id.aiHeader)
        tvAiReply = view.findViewById(R.id.tvAiReply)
        loadingProgress = view.findViewById(R.id.loadingProgress)
        btnGenerate = view.findViewById(R.id.btnGenerate)
        tvDocsList = view.findViewById(R.id.tvDocsList)
        tvServerStatus = view.findViewById(R.id.tvServerStatus)
        viewServerStatus = view.findViewById(R.id.viewServerStatus)
        
        btnCaptureScreenshot = view.findViewById(R.id.btnCaptureScreenshot)
        btnRetryOcr = view.findViewById(R.id.btnRetryOcr)
        ivScreenshotPreview = view.findViewById(R.id.ivScreenshotPreview)
        llScreenshotStatus = view.findViewById(R.id.llScreenshotStatus)
        tvScreenshotStatus = view.findViewById(R.id.tvScreenshotStatus)
        tvExtractedText = view.findViewById(R.id.tvExtractedText)
        toolsLoader = view.findViewById(R.id.toolsLoader)

        // Spam UI Initialization
        layoutSpam = view.findViewById(R.id.layoutSpam)
        etSpamText = view.findViewById(R.id.etSpamText)
        etSpamCount = view.findViewById(R.id.etSpamCount)
        etSpamInterval = view.findViewById(R.id.etSpamInterval)
        btnStartSpam = view.findViewById(R.id.btnStartSpam)
        btnCancelSpam = view.findViewById(R.id.btnCancelSpam)

        view.findViewById<ImageButton>(R.id.btnOpenSpam).setOnClickListener {
            layoutSpam.isVisible = !layoutSpam.isVisible
        }

        btnStartSpam.setOnClickListener { startSpamming() }
        btnCancelSpam.setOnClickListener {
            spamJob?.cancel()
            layoutSpam.isGone = true
        }

        setupQwertyTab(view)

        // Tab Selection
        view.findViewById<ImageButton>(R.id.tabMain).setOnClickListener { viewFlipper.displayedChild = 0 }
        view.findViewById<ImageButton>(R.id.tabKeys).setOnClickListener { viewFlipper.displayedChild = 1 }
        view.findViewById<ImageButton>(R.id.tabQwerty).setOnClickListener { viewFlipper.displayedChild = 2 }
        view.findViewById<ImageButton>(R.id.tabClipboard).setOnClickListener { viewFlipper.displayedChild = 3 }
        view.findViewById<ImageButton>(R.id.tabScreenshot).setOnClickListener { viewFlipper.displayedChild = 4 }
        
        view.findViewById<ImageButton>(R.id.btnSwitchInput).setOnClickListener {
            val imm = getSystemService(InputMethodManager::class.java)
            imm?.showInputMethodPicker()
        }

        // AI Tools
        view.findViewById<Button>(R.id.btnSelectAll).setOnClickListener { selectAllText() }
        view.findViewById<Button>(R.id.btnAllCaps).setOnClickListener { transformSelectedText { it.uppercase() } }
        view.findViewById<Button>(R.id.btnTitleCase).setOnClickListener { transformSelectedText { it.lowercase().split(" ").joinToString(" ") { w -> w.replaceFirstChar { c -> c.uppercase() } } } }
        view.findViewById<Button>(R.id.btnBold).setOnClickListener { transformSelectedText { "**$it**" } }
        
        view.findViewById<Button>(R.id.btnFormal).setOnClickListener { selectAllAndAiTransform(AiPrompts.FORMAL) }
        view.findViewById<Button>(R.id.btnGrammar).setOnClickListener { selectAllAndAiTransform(AiPrompts.GRAMMAR) }
        view.findViewById<Button>(R.id.btnProfessional).setOnClickListener { selectAllAndAiTransform(AiPrompts.PROFESSIONAL) }
        view.findViewById<Button>(R.id.btnReply).setOnClickListener { selectAllAndAiTransform(AiPrompts.REPLY) }

        // History
        val rvHistory = view.findViewById<RecyclerView>(R.id.rvHistory)
        historyAdapter = HistoryAdapter(historyList, { reply -> currentInputConnection?.commitText(reply, 1) }, { item ->
            historyList.remove(item)
            historyAdapter.updateData(historyList)
        })
        rvHistory.layoutManager = LinearLayoutManager(this)
        rvHistory.adapter = historyAdapter

        view.findViewById<Button>(R.id.btnClearAll).setOnClickListener {
            historyList.clear()
            historyAdapter.updateData(historyList)
        }

        btnGenerate.setOnClickListener {
            val clipboard = getSystemService(ClipboardManager::class.java)
            val text = clipboard?.primaryClip?.getItemAt(0)?.text?.toString()
            if (!text.isNullOrBlank()) generateAiReply(text) else Toast.makeText(this, "Copy text first", Toast.LENGTH_SHORT).show()
        }

        tvAiReply.setOnClickListener {
            currentInputConnection?.commitText(tvAiReply.text, 1)
            aiHeader.isGone = true
        }

        btnCaptureScreenshot.setOnClickListener { captureAndProcessScreenshot() }
        btnRetryOcr.setOnClickListener { lastCapturedBitmap?.let { processImageForOcr(it) } }

        refreshDocsInfo()
        return view
    }

    private fun startSpamming() {
        val text = etSpamText.text.toString()
        val count = etSpamCount.text.toString().toIntOrNull() ?: 0
        val interval = etSpamInterval.text.toString().toFloatOrNull() ?: 1.0f
        
        if (text.isEmpty() || count <= 0) {
            Toast.makeText(this, "Invalid input", Toast.LENGTH_SHORT).show()
            return
        }

        spamJob?.cancel()
        spamJob = serviceScope.launch {
            btnStartSpam.isEnabled = false
            btnStartSpam.text = "Spamming..."
            for (i in 1..count) {
                if (!isActive) break
                currentInputConnection?.commitText(text, 1)
                currentInputConnection?.sendKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_ENTER))
                delay((interval * 1000).toLong())
            }
            btnStartSpam.isEnabled = true
            btnStartSpam.text = "Start Spam"
            Toast.makeText(this@AIKeyboardService, "Spam finished", Toast.LENGTH_SHORT).show()
        }
    }

    private fun setupQwertyTab(view: View) {
        val layoutLetters = view.findViewById<LinearLayout>(R.id.layoutLetters)
        val layoutSymbols = view.findViewById<LinearLayout>(R.id.layoutSymbols)

        val keyClickListener = View.OnClickListener { v ->
            val b = v as Button
            val text = b.text.toString()
            when (text) {
                "Space" -> {
                    currentInputConnection?.commitText(" ", 1)
                    updateSuggestions("")
                }
                "⌫" -> {
                    currentInputConnection?.sendKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_DEL))
                    updateSuggestionsFromCurrentWord()
                }
                "↵" -> {
                    currentInputConnection?.sendKeyEvent(KeyEvent(KeyEvent.ACTION_DOWN, KeyEvent.KEYCODE_ENTER))
                    updateSuggestions("")
                }
                "⇧" -> {
                    isShifted = !isShifted
                    updateKeyLabels(layoutLetters)
                }
                "?123" -> {
                    layoutLetters.isVisible = false
                    layoutSymbols.isVisible = true
                }
                "ABC" -> {
                    layoutSymbols.isVisible = false
                    layoutLetters.isVisible = true
                }
                else -> {
                    currentInputConnection?.commitText(text, 1)
                    if (isShifted) {
                        isShifted = false
                        updateKeyLabels(layoutLetters)
                    }
                    updateSuggestionsFromCurrentWord()
                }
            }
        }

        setListenersRecursively(layoutLetters, keyClickListener)
        setListenersRecursively(layoutSymbols, keyClickListener)
        updateSuggestions("")
    }

    private fun updateSuggestionsFromCurrentWord() {
        val ic = currentInputConnection ?: return
        val before = ic.getTextBeforeCursor(20, 0)
        if (before == null) {
            updateSuggestions("")
            return
        }
        val lastWord = before.split(" ").lastOrNull() ?: ""
        updateSuggestions(lastWord)
    }

    private fun updateSuggestions(query: String) {
        val container = viewFlipper.findViewById<LinearLayout>(R.id.suggestionContainer) ?: return
        container.removeAllViews()
        
        val filtered = if (query.isBlank()) {
            commonWords.take(5)
        } else {
            commonWords.filter { it.startsWith(query, ignoreCase = true) }.take(5)
        }

        for (word in filtered) {
            val tv = TextView(this)
            tv.text = word
            tv.setTextColor(Color.WHITE)
            tv.setPadding(32, 0, 32, 0)
            tv.textSize = 16f
            tv.layoutParams = LinearLayout.LayoutParams(ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.MATCH_PARENT)
            tv.gravity = android.view.Gravity.CENTER
            tv.setBackgroundResource(android.R.drawable.list_selector_background)
            tv.setOnClickListener {
                replaceCurrentWord(word)
            }
            container.addView(tv)
        }
    }

    private fun replaceCurrentWord(newWord: String) {
        val ic = currentInputConnection ?: return
        val before = ic.getTextBeforeCursor(20, 0) ?: ""
        val lastWord = before.split(" ").lastOrNull() ?: ""
        ic.deleteSurroundingText(lastWord.length, 0)
        ic.commitText(newWord + " ", 1)
        updateSuggestions("")
    }

    private fun setListenersRecursively(view: View, listener: View.OnClickListener) {
        if (view is Button) {
            view.setOnClickListener(listener)
        } else if (view is ViewGroup) {
            for (i in 0 until view.childCount) {
                setListenersRecursively(view.getChildAt(i), listener)
            }
        }
    }

    private fun updateKeyLabels(layout: ViewGroup) {
        for (i in 0 until layout.childCount) {
            val child = layout.getChildAt(i)
            if (child is Button && child.text.length == 1 && Character.isLetter(child.text[0])) {
                child.text = if (isShifted) child.text.toString().uppercase() else child.text.toString().lowercase()
            } else if (child is ViewGroup) {
                updateKeyLabels(child)
            }
        }
    }

    private fun selectAllText() {
        currentInputConnection?.setSelection(0, 10000)
    }

    private fun selectAllAndAiTransform(instruction: String) {
        selectAllText()
        Handler(Looper.getMainLooper()).postDelayed({ aiTransformSelectedText(instruction) }, 150)
    }

    private fun aiTransformSelectedText(instruction: String) {
        val ic = currentInputConnection ?: return
        val selectedText = ic.getSelectedText(0)
        if (selectedText.isNullOrBlank()) {
            Toast.makeText(this, "Select text first", Toast.LENGTH_SHORT).show()
            return
        }

        serviceScope.launch {
            toolsLoader.isVisible = true
            try {
                val response = withContext(Dispatchers.IO) {
                    apiService.chatDirect(ChatRequest(message = "$instruction \"$selectedText\""))
                }
                ic.commitText(response.response, 1)
            } catch (e: Exception) {
                Toast.makeText(this@AIKeyboardService, "AI Error: ${e.message}", Toast.LENGTH_LONG).show()
            } finally {
                toolsLoader.isGone = true
            }
        }
    }

    private fun captureAndProcessScreenshot() {
        val intent = ScreenshotService.projectionIntent ?: return Toast.makeText(this, "Grant permission in App", Toast.LENGTH_SHORT).show()
        llScreenshotStatus.isVisible = true
        tvScreenshotStatus.text = "Preparing..."
        
        try {
            val serviceIntent = Intent(this, ScreenshotService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(serviceIntent) else startService(serviceIntent)
        } catch (e: Exception) { return }

        Handler(Looper.getMainLooper()).postDelayed({
            try {
                performCapture(intent)
            } catch (e: Exception) {
                tvScreenshotStatus.text = "Error: ${e.message}"
                btnRetryOcr.isVisible = true
                stopService(Intent(this, ScreenshotService::class.java))
            }
        }, 1500)
    }

    private fun performCapture(intent: Intent) {
        val projectionManager = getSystemService(MediaProjectionManager::class.java) ?: return
        if (currentMediaProjection == null) {
            currentMediaProjection = projectionManager.getMediaProjection(Activity.RESULT_OK, intent)
            currentMediaProjection?.registerCallback(object : MediaProjection.Callback() {
                override fun onStop() { currentMediaProjection = null }
            }, Handler(Looper.getMainLooper()))
        }
        
        val mediaProjection = currentMediaProjection ?: return
        val windowManager = getSystemService(WindowManager::class.java) ?: return
        val metrics = DisplayMetrics()
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            val bounds = windowManager.currentWindowMetrics.bounds
            metrics.widthPixels = bounds.width()
            metrics.heightPixels = bounds.height()
            metrics.densityDpi = resources.configuration.densityDpi
        } else {
            @Suppress("DEPRECATION")
            windowManager.defaultDisplay.getRealMetrics(metrics)
        }
        
        val imageReader = ImageReader.newInstance(metrics.widthPixels, metrics.heightPixels, PixelFormat.RGBA_8888, 2)
        val virtualDisplay = mediaProjection.createVirtualDisplay("AIKeyboardCapture", metrics.widthPixels, metrics.heightPixels, metrics.densityDpi, DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR, imageReader.surface, null, null)

        imageReader.setOnImageAvailableListener({ reader ->
            val image = reader.acquireLatestImage() ?: return@setOnImageAvailableListener
            try {
                val planes = image.planes
                val buffer = planes[0].buffer
                val pixelStride = planes[0].pixelStride
                val rowStride = planes[0].rowStride
                val bitmap = Bitmap.createBitmap(metrics.widthPixels + (rowStride - pixelStride * metrics.widthPixels) / pixelStride, metrics.heightPixels, Bitmap.Config.ARGB_8888)
                bitmap.copyPixelsFromBuffer(buffer)
                
                val captureHeightPx = (AppConfig.getScreenshotHeight(this) * (metrics.densityDpi / 160f)).toInt().coerceIn(100, metrics.heightPixels)
                val startY = (metrics.heightPixels * 0.25).toInt()
                val cropped = Bitmap.createBitmap(bitmap, 0, startY, metrics.widthPixels, captureHeightPx.coerceAtMost(metrics.heightPixels - startY))
                
                Handler(Looper.getMainLooper()).post {
                    lastCapturedBitmap = cropped
                    ivScreenshotPreview.setImageBitmap(cropped)
                    llScreenshotStatus.isGone = true
                    processImageForOcr(cropped)
                }
            } catch (e: Exception) { } finally {
                image.close()
                reader.close()
                virtualDisplay.release()
                stopService(Intent(this, ScreenshotService::class.java))
            }
        }, Handler(Looper.getMainLooper()))
    }

    private fun processImageForOcr(bitmap: Bitmap) {
        llScreenshotStatus.isVisible = true
        tvScreenshotStatus.text = "Extracting text..."
        recognizer.process(InputImage.fromBitmap(bitmap, 0))
            .addOnSuccessListener { visionText ->
                tvExtractedText.text = visionText.text
                if (visionText.text.isNotBlank()) generateAiReply(visionText.text) else tvScreenshotStatus.text = "No text found"
                llScreenshotStatus.isGone = true
            }
            .addOnFailureListener {
                tvScreenshotStatus.text = "OCR Failed"
                btnRetryOcr.isVisible = true
            }
    }

    private fun transformSelectedText(transform: (String) -> String) {
        val selected = currentInputConnection?.getSelectedText(0)
        if (!selected.isNullOrEmpty()) currentInputConnection?.commitText(transform(selected.toString()), 1) else Toast.makeText(this, "Select text first", Toast.LENGTH_SHORT).show()
    }

    private fun startStatusUpdates() {
        statusJob = serviceScope.launch {
            while (isActive) {
                try {
                    val response = withContext(Dispatchers.IO) { apiService.checkHealth() }
                    updateStatusUi(response.status == "healthy")
                } catch (e: Exception) { updateStatusUi(false) }
                delay(10000)
            }
        }
    }

    private fun updateStatusUi(isLive: Boolean) {
        tvServerStatus.text = if (isLive) "Live" else "Offline"
        viewServerStatus.setBackgroundColor(if (isLive) Color.GREEN else Color.RED)
    }

    private fun refreshDocsInfo() {
        if (prefsManager.getAccessToken() == null) {
            tvDocsList.text = "Please login in App"
            return
        }
        serviceScope.launch {
            try {
                val docs = withContext(Dispatchers.IO) { apiService.listDocuments() }
                tvDocsList.text = docs.joinToString(", ") { it.file_name }.ifEmpty { "No documents found" }
            } catch (e: Exception) { tvDocsList.text = "Error loading docs" }
        }
    }

    override fun onPrimaryClipChanged() {}

    private fun generateAiReply(text: String) {
        if (prefsManager.getAccessToken() == null) {
            Toast.makeText(this, "Please login in App", Toast.LENGTH_SHORT).show()
            return
        }
        serviceScope.launch {
            aiHeader.isVisible = true
            loadingProgress.isVisible = true
            tvAiReply.text = ""
            try {
                val profile = prefsManager.getResumeProfile()
                val prompt = if (profile != null) "System Instruction: ${profile.systemInstruction}\n\nMy name is ${profile.name}, email ${profile.email}.\n\nContext/Text: $text" else text
                val response = withContext(Dispatchers.IO) { apiService.chat(ChatRequest(message = prompt)) }
                tvAiReply.text = response.response
                historyList.add(0, HistoryItem(originalText = text, aiReply = response.response))
                historyAdapter.updateData(historyList)
            } catch (e: Exception) { tvAiReply.text = "Error: ${e.message}" } finally { loadingProgress.isGone = true }
        }
    }
}
