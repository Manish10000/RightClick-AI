package com.example.aikeyboard.ui.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageButton
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.aikeyboard.R
import com.example.aikeyboard.data.remote.DocumentItem

class DocumentAdapter(
    private var documents: List<DocumentItem>,
    private val onDeleteClick: (DocumentItem) -> Unit
) : RecyclerView.Adapter<DocumentAdapter.ViewHolder>() {

    class ViewHolder(view: View) : RecyclerView.ViewHolder(view) {
        val tvFileName: TextView = view.findViewById(R.id.tvFileName)
        val tvFileInfo: TextView = view.findViewById(R.id.tvFileInfo)
        val btnDelete: ImageButton = view.findViewById(R.id.btnDelete)
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_document, parent, false)
        return ViewHolder(view)
    }

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        val doc = documents[position]
        holder.tvFileName.text = doc.file_name
        
        val sizeKb = (doc.file_size ?: 0L) / 1024
        val chunks = doc.num_chunks ?: 0
        holder.tvFileInfo.text = "Size: $sizeKb KB | Chunks: $chunks"

        holder.btnDelete.setOnClickListener { 
            onDeleteClick(doc) 
        }
    }

    override fun getItemCount() = documents.size

    fun updateDocuments(newDocuments: List<DocumentItem>) {
        documents = newDocuments
        notifyDataSetChanged()
    }
}
