package com.example.aikeyboard

import android.app.Activity
import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.PixelFormat
import android.hardware.display.DisplayManager
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.provider.OpenableColumns
import android.provider.Settings
import android.util.DisplayMetrics
import android.view.View
import android.view.WindowManager
import android.view.inputmethod.InputMethodManager
import android.widget.*
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.aikeyboard.data.local.EncryptedPrefsManager
import com.example.aikeyboard.data.model.ResumeProfile
import com.example.aikeyboard.data.remote.*
import com.example.aikeyboard.service.ScreenshotService
import com.example.aikeyboard.ui.adapter.DocumentAdapter
import com.example.aikeyboard.utils.AppConfig
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.latin.TextRecognizerOptions
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import okhttp3.Interceptor
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.RequestBody.Companion.asRequestBody
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.TimeUnit

class MainActivity : AppCompatActivity() {

    private lateinit var prefsManager: EncryptedPrefsManager
    private lateinit var documentAdapter: DocumentAdapter
    private val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)
    
    private val projectionLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        if (result.resultCode == Activity.RESULT_OK && result.data != null) {
            ScreenshotService.projectionIntent = result.data
            Toast.makeText(this, "Screenshot permission granted!", Toast.LENGTH_SHORT).show()
        }
    }

    private fun getApiService(): ApiService {
        val timeout = prefsManager.getTimeout()
        val okHttpClient = OkHttpClient.Builder()
            .connectTimeout(timeout, TimeUnit.SECONDS)
            .readTimeout(timeout, TimeUnit.SECONDS)
            .writeTimeout(timeout, TimeUnit.SECONDS)
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

    private val filePickerLauncher = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            result.data?.data?.let { uri ->
                uploadDocument(uri)
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        prefsManager = EncryptedPrefsManager(this)

        val etBaseUrl = findViewById<EditText>(R.id.etBaseUrl)
        val etTimeout = findViewById<EditText>(R.id.etTimeout)
        val sbScreenshotHeight = findViewById<SeekBar>(R.id.sbScreenshotHeight)
        val tvHeightValue = findViewById<TextView>(R.id.tvHeightValue)
        
        // Auth Views
        val etAuthEmail = findViewById<EditText>(R.id.etAuthEmail)
        val etAuthPassword = findViewById<EditText>(R.id.etAuthPassword)
        val etAuthFullName = findViewById<EditText>(R.id.etAuthFullName)
        val btnLogin = findViewById<Button>(R.id.btnLogin)
        val btnRegister = findViewById<Button>(R.id.btnRegister)
        val btnLogout = findViewById<Button>(R.id.btnLogout)

        // Profile Views
        val etName = findViewById<EditText>(R.id.etName)
        val etEmail = findViewById<EditText>(R.id.etEmail)
        val etSystemInstruction = findViewById<EditText>(R.id.etSystemInstruction)
        
        val btnSave = findViewById<Button>(R.id.btnSaveProfile)
        val btnUpload = findViewById<Button>(R.id.btnUploadDoc)
        val rvDocuments = findViewById<RecyclerView>(R.id.rvDocuments)
        
        val btnTestCapture = findViewById<Button>(R.id.btnTestCapture)
        val llTestResult = findViewById<LinearLayout>(R.id.llTestResult)
        val ivTestPreview = findViewById<ImageView>(R.id.ivTestPreview)
        val tvTestExtracted = findViewById<TextView>(R.id.tvTestExtracted)

        // Setup RecyclerView
        documentAdapter = DocumentAdapter(emptyList()) { doc ->
            deleteDocument(doc.id)
        }
        rvDocuments.layoutManager = LinearLayoutManager(this)
        rvDocuments.adapter = documentAdapter

        // Load existing settings
        etBaseUrl.setText(prefsManager.getBaseUrl() ?: "")
        etTimeout.setText(prefsManager.getTimeout().toString())
        sbScreenshotHeight.progress = prefsManager.getScreenshotHeight()
        tvHeightValue.text = "${sbScreenshotHeight.progress}dp"

        sbScreenshotHeight.setOnSeekBarChangeListener(object : SeekBar.OnSeekBarChangeListener {
            override fun onProgressChanged(seekBar: SeekBar?, progress: Int, fromUser: Boolean) {
                tvHeightValue.text = "${progress}dp"
            }
            override fun onStartTrackingTouch(seekBar: SeekBar?) {}
            override fun onStopTrackingTouch(seekBar: SeekBar?) {}
        })

        prefsManager.getResumeProfile()?.let {
            etName.setText(it.name)
            etEmail.setText(it.email)
            etSystemInstruction.setText(it.systemInstruction)
        }

        updateAuthUi(btnLogin, btnRegister, btnLogout)

        btnLogin.setOnClickListener {
            val email = etAuthEmail.text.toString()
            val password = etAuthPassword.text.toString()
            if (email.isNotBlank() && password.isNotBlank()) {
                login(email, password, btnLogin, btnRegister, btnLogout)
            }
        }

        btnRegister.setOnClickListener {
            val email = etAuthEmail.text.toString()
            val password = etAuthPassword.text.toString()
            val fullName = etAuthFullName.text.toString()
            if (email.isNotBlank() && password.isNotBlank()) {
                register(email, password, fullName)
            }
        }

        btnLogout.setOnClickListener {
            prefsManager.clearAuth()
            updateAuthUi(btnLogin, btnRegister, btnLogout)
            documentAdapter.updateDocuments(emptyList())
        }

        btnSave.setOnClickListener {
            if (ScreenshotService.projectionIntent == null) {
                val mediaProjectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
                projectionLauncher.launch(mediaProjectionManager.createScreenCaptureIntent())
            }

            prefsManager.saveBaseUrl(etBaseUrl.text.toString().trim().ifEmpty { null })
            prefsManager.saveTimeout(etTimeout.text.toString().trim().toLongOrNull() ?: AppConfig.DEFAULT_TIMEOUT_SECONDS)
            prefsManager.saveScreenshotHeight(sbScreenshotHeight.progress)

            val profile = ResumeProfile(
                name = etName.text.toString(),
                email = etEmail.text.toString(),
                systemInstruction = etSystemInstruction.text.toString()
            )
            prefsManager.saveResumeProfile(profile)
            Toast.makeText(this, "Settings Saved", Toast.LENGTH_SHORT).show()
            refreshDocuments()
        }

        btnTestCapture.setOnClickListener {
            val intent = ScreenshotService.projectionIntent ?: return@setOnClickListener Toast.makeText(this, "Grant permission first", Toast.LENGTH_SHORT).show()
            llTestResult.visibility = View.VISIBLE
            try {
                val serviceIntent = Intent(this, ScreenshotService::class.java)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) startForegroundService(serviceIntent) else startService(serviceIntent)
            } catch (e: Exception) { return@setOnClickListener }

            Handler(Looper.getMainLooper()).postDelayed({
                performTestCapture(intent, ivTestPreview, tvTestExtracted)
            }, 1500)
        }

        btnUpload.setOnClickListener {
            filePickerLauncher.launch(Intent(Intent.ACTION_GET_CONTENT).apply { type = "*/*" })
        }

        findViewById<Button>(R.id.btnEnableKeyboard).setOnClickListener { startActivity(Intent(Settings.ACTION_INPUT_METHOD_SETTINGS)) }
        findViewById<Button>(R.id.btnSwitchKeyboard).setOnClickListener {
            val imm = getSystemService(InputMethodManager::class.java)
            imm?.showInputMethodPicker()
        }

        refreshDocuments()
    }

    private fun updateAuthUi(login: Button, register: Button, logout: Button) {
        val isLoggedIn = prefsManager.getAccessToken() != null
        login.visibility = if (isLoggedIn) View.GONE else View.VISIBLE
        register.visibility = if (isLoggedIn) View.GONE else View.VISIBLE
        logout.visibility = if (isLoggedIn) View.VISIBLE else View.GONE
    }

    private fun login(email: String, pass: String, l: Button, r: Button, out: Button) {
        lifecycleScope.launch {
            try {
                val response = getApiService().login(LoginRequest(email, pass))
                prefsManager.saveAccessToken(response.access_token)
                prefsManager.saveRefreshToken(response.refresh_token)
                updateAuthUi(l, r, out)
                Toast.makeText(this@MainActivity, "Logged in!", Toast.LENGTH_SHORT).show()
                refreshDocuments()
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "Login failed: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun register(email: String, pass: String, name: String) {
        lifecycleScope.launch {
            try {
                getApiService().register(RegisterRequest(email, pass, name))
                Toast.makeText(this@MainActivity, "Registered! Now login.", Toast.LENGTH_SHORT).show()
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "Register failed: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun performTestCapture(intent: Intent, preview: ImageView, resultText: TextView) {
        val projectionManager = getSystemService(Context.MEDIA_PROJECTION_SERVICE) as MediaProjectionManager
        val mediaProjection = projectionManager.getMediaProjection(Activity.RESULT_OK, intent) ?: return
        
        val windowManager = getSystemService(Context.WINDOW_SERVICE) as WindowManager
        val metrics = DisplayMetrics()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
            val windowMetrics = windowManager.currentWindowMetrics
            val bounds = windowMetrics.bounds
            metrics.widthPixels = bounds.width()
            metrics.heightPixels = bounds.height()
            metrics.densityDpi = resources.configuration.densityDpi
        } else {
            @Suppress("DEPRECATION")
            windowManager.defaultDisplay.getRealMetrics(metrics)
        }
        
        val imageReader = ImageReader.newInstance(metrics.widthPixels, metrics.heightPixels, PixelFormat.RGBA_8888, 2)
        val virtualDisplay = mediaProjection.createVirtualDisplay("TestCapture", metrics.widthPixels, metrics.heightPixels, metrics.densityDpi, DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR, imageReader.surface, null, null)

        imageReader.setOnImageAvailableListener({ reader ->
            val image = reader.acquireLatestImage() ?: return@setOnImageAvailableListener
            try {
                val planes = image.planes
                val buffer = planes[0].buffer
                val pixelStride = planes[0].pixelStride
                val rowStride = planes[0].rowStride
                val bitmap = Bitmap.createBitmap(metrics.widthPixels + (rowStride - pixelStride * metrics.widthPixels) / pixelStride, metrics.heightPixels, Bitmap.Config.ARGB_8888)
                bitmap.copyPixelsFromBuffer(buffer)
                
                val captureHeightPx = (findViewById<SeekBar>(R.id.sbScreenshotHeight).progress * (metrics.densityDpi / 160f)).toInt().coerceIn(100, metrics.heightPixels)
                val cropped = Bitmap.createBitmap(bitmap, 0, metrics.heightPixels - captureHeightPx, metrics.widthPixels, captureHeightPx)
                
                Handler(Looper.getMainLooper()).post {
                    preview.setImageBitmap(cropped)
                    recognizer.process(InputImage.fromBitmap(cropped, 0))
                        .addOnSuccessListener { resultText.text = "Extracted: ${it.text}" }
                }
            } catch (e: Exception) { } finally {
                image.close()
                reader.close()
                virtualDisplay.release()
                mediaProjection.stop()
                stopService(Intent(this, ScreenshotService::class.java))
            }
        }, Handler(Looper.getMainLooper()))
    }

    private fun refreshDocuments() {
        if (prefsManager.getAccessToken() == null) return
        lifecycleScope.launch {
            try {
                val docs = getApiService().listDocuments()
                documentAdapter.updateDocuments(docs)
            } catch (e: Exception) { }
        }
    }

    private fun deleteDocument(docId: String) {
        lifecycleScope.launch {
            try {
                val response = getApiService().deleteDocument(docId)
                if (response.success) {
                    Toast.makeText(this@MainActivity, "Deleted", Toast.LENGTH_SHORT).show()
                    delay(500)
                    refreshDocuments()
                }
            } catch (e: Exception) { }
        }
    }

    private fun uploadDocument(uri: Uri) {
        lifecycleScope.launch {
            try {
                val fileName = getFileName(uri) ?: "upload.pdf"
                val file = getFileFromUri(uri, fileName) ?: return@launch
                val body = MultipartBody.Part.createFormData("file", file.name, file.asRequestBody("application/octet-stream".toMediaTypeOrNull()))
                val response = getApiService().uploadDocument(body)
                if (response.success) {
                    Toast.makeText(this@MainActivity, "Uploaded", Toast.LENGTH_SHORT).show()
                    delay(500)
                    refreshDocuments()
                }
            } catch (e: Exception) {
                Toast.makeText(this@MainActivity, "Upload Error: ${e.message}", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun getFileName(uri: Uri): String? {
        contentResolver.query(uri, null, null, null, null)?.use { cursor ->
            if (cursor.moveToFirst()) {
                val index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                if (index != -1) return cursor.getString(index)
            }
        }
        return null
    }

    private fun getFileFromUri(uri: Uri, fileName: String): File? {
        val inputStream = contentResolver.openInputStream(uri) ?: return null
        val file = File(cacheDir, fileName)
        FileOutputStream(file).use { inputStream.copyTo(it) }
        inputStream.close()
        return file
    }
}
