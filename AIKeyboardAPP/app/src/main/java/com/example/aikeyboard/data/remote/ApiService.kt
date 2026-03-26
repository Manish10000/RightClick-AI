package com.example.aikeyboard.data.remote

import okhttp3.MultipartBody
import retrofit2.http.*

interface ApiService {
    // Authentication
    @POST("auth/register")
    suspend fun register(@Body request: RegisterRequest): AuthResponse

    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): AuthResponse

    // Health
    @GET("health")
    suspend fun checkHealth(): HealthResponse

    // Document Management
    @Multipart
    @POST("upload")
    suspend fun uploadDocument(@Part file: MultipartBody.Part): UploadResponse

    @GET("documents")
    suspend fun listDocuments(): List<DocumentItem>

    @DELETE("documents/{id}")
    suspend fun deleteDocument(@Path("id") id: String): DeleteResponse

    // Chat & RAG
    @POST("chat")
    suspend fun chat(@Body request: ChatRequest): ChatResponse

    @POST("chat/direct")
    suspend fun chatDirect(@Body request: ChatRequest): ChatResponse

    @POST("search")
    suspend fun search(@Body request: SearchRequest): SearchResponse

    @GET("stats")
    suspend fun getStats(): StatsResponse

    @GET("/")
    suspend fun getRootInfo(): RootInfoResponse
}

// Auth Models
data class RegisterRequest(
    val email: String,
    val password: String,
    val full_name: String
)

data class LoginRequest(
    val email: String,
    val password: String
)

data class AuthResponse(
    val access_token: String,
    val refresh_token: String,
    val token_type: String
)

data class HealthResponse(
    val status: String,
    val version: String,
    val mongodb_connected: Boolean? = null,
    val ollama_available: Boolean? = null,
    val total_documents: Int? = null
)

data class UploadResponse(
    val success: Boolean,
    val document_id: String?,
    val file_name: String?,
    val num_chunks: Int?,
    val message: String
)

data class SearchRequest(
    val query: String,
    val top_k: Int = 5,
    val similarity_threshold: Float = 0.0f
)

data class SearchResponse(
    val query: String,
    val results: List<SearchResult>,
    val total_results: Int,
    val search_time_ms: Double
)

data class SearchResult(
    val content: String,
    val file_path: String,
    val chunk_index: Int,
    val score: Double,
    val metadata: Map<String, Any>
)

data class ChatRequest(
    val message: String,
    val context_chunks: Int = 3,
    val model: String = "llama3.1:8b"
)

data class ChatResponse(
    val response: String,
    val sources: List<SearchResult> = emptyList(),
    val model: String,
    val used_rag: Boolean = false,
    val num_sources: Int = 0
)

data class DocumentItem(
    val id: String,
    val file_name: String,
    val file_path: String? = null,
    val file_size: Long? = null,
    val file_type: String? = null,
    val num_chunks: Int? = null,
    val uploaded_at: String? = null,
    val processed: Boolean? = null
)

data class DeleteResponse(
    val success: Boolean,
    val document_id: String,
    val message: String
)

data class StatsResponse(
    val total_documents: Int,
    val total_chunks: Int,
    val total_size_bytes: Long,
    val documents: List<DocumentItem>
)

data class RootInfoResponse(
    val name: String,
    val version: String,
    val status: String
)
