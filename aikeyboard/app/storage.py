"""
MongoDB storage operations for AI Keyboard
"""
from pymongo import MongoClient, ASCENDING, DESCENDING
from app.config import MONGO_URI, DB_NAME, COLLECTION_NAME
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Storage:
    """Handles all MongoDB operations"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        try:
            self.client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.server_info()
            self.db = self.client[DB_NAME]
            self.nodes = self.db["nodes"]
            self.clusters = self.db["clusters"]
            self.metadata = self.db["metadata"]
            
            # Create indices for better performance
            self._create_indices()
            logger.info(f"Connected to MongoDB: {DB_NAME}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def _create_indices(self):
        """Create database indices for performance"""
        # Node indices
        self.nodes.create_index([("file_path", ASCENDING)])
        self.nodes.create_index([("cluster_id", ASCENDING)])
        self.nodes.create_index([("is_summary", ASCENDING)])
        
        # Cluster indices
        self.clusters.create_index([("level", ASCENDING)])
        self.clusters.create_index([("parent", ASCENDING)])
    
    # Node operations
    def save_node(self, node_data: Dict[str, Any]) -> str:
        """Save a node to database"""
        result = self.nodes.insert_one(node_data)
        return str(result.inserted_id)
    
    def get_node(self, node_id: str) -> Optional[Dict]:
        """Get a node by ID"""
        return self.nodes.find_one({"_id": node_id})
    
    def get_all_nodes(self) -> List[Dict]:
        """Get all nodes"""
        return list(self.nodes.find())
    
    def get_nodes_by_cluster(self, cluster_id: str) -> List[Dict]:
        """Get all nodes in a cluster"""
        return list(self.nodes.find({"cluster_id": cluster_id}))
    
    def get_summary_nodes(self) -> List[Dict]:
        """Get all summary nodes"""
        return list(self.nodes.find({"is_summary": True}))
    
    def get_detail_nodes(self) -> List[Dict]:
        """Get all detail nodes"""
        return list(self.nodes.find({"is_summary": False}))
    
    def update_node(self, node_id: str, update_data: Dict[str, Any]):
        """Update a node"""
        self.nodes.update_one({"_id": node_id}, {"$set": update_data})
    
    def delete_node(self, node_id: str):
        """Delete a node"""
        self.nodes.delete_one({"_id": node_id})
    
    # Cluster operations
    def save_cluster(self, cluster_data: Dict[str, Any]) -> str:
        """Save a cluster"""
        result = self.clusters.insert_one(cluster_data)
        return str(result.inserted_id)
    
    def get_cluster(self, cluster_id: str) -> Optional[Dict]:
        """Get a cluster by ID"""
        return self.clusters.find_one({"_id": cluster_id})
    
    def get_all_clusters(self) -> List[Dict]:
        """Get all clusters"""
        return list(self.clusters.find())
    
    def get_clusters_by_level(self, level: int) -> List[Dict]:
        """Get clusters by level"""
        return list(self.clusters.find({"level": level}))
    
    def get_clusters_by_parent(self, parent_id: str) -> List[Dict]:
        """Get child clusters"""
        return list(self.clusters.find({"parent": parent_id}))
    
    def update_cluster(self, cluster_id: str, update_data: Dict[str, Any]):
        """Update a cluster"""
        self.clusters.update_one({"_id": cluster_id}, {"$set": update_data})
    
    # Metadata operations
    def save_metadata(self, key: str, value: Any):
        """Save metadata"""
        self.metadata.update_one(
            {"key": key},
            {"$set": {"value": value}},
            upsert=True
        )
    
    def save_document_metadata(self, doc_data: Dict[str, Any]):
        """Save document metadata"""
        self.metadata.insert_one(doc_data)
    
    def get_metadata(self, key: str) -> Optional[Any]:
        """Get metadata"""
        result = self.metadata.find_one({"key": key})
        return result["value"] if result else None
    
    # Database management
    def clear_database(self):
        """Clear all data from database"""
        self.nodes.delete_many({})
        self.clusters.delete_many({})
        self.metadata.delete_many({})
        logger.info("Database cleared")
    
    def get_stats(self) -> Dict[str, int]:
        """Get database statistics"""
        return {
            "total_nodes": self.nodes.count_documents({}),
            "summary_nodes": self.nodes.count_documents({"is_summary": True}),
            "detail_nodes": self.nodes.count_documents({"is_summary": False}),
            "total_clusters": self.clusters.count_documents({}),
            "l1_clusters": self.clusters.count_documents({"level": 1}),
            "l2_clusters": self.clusters.count_documents({"level": 2})
        }
    
    def close(self):
        """Close MongoDB connection"""
        self.client.close()
        logger.info("MongoDB connection closed")


# Global storage instance
_storage = None


def get_storage() -> Storage:
    """Get or create global storage instance"""
    global _storage
    if _storage is None:
        _storage = Storage()
    return _storage
