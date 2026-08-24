import structlog

from app.core.config import settings

logger = structlog.get_logger()


class ChromaDBStore:
    """Wrapper para ChromaDB: indexación y búsqueda de transacciones"""

    def __init__(self):
        self._client = None
        self._collection_prefix = "txns_"

    def _get_client(self):
        if self._client is None:
            try:
                import chromadb
                self._client = chromadb.PersistentClient(path=settings.CHROMADB_PATH)
            except ImportError:
                logger.warning("chromadb_not_installed")
                return None
            except Exception as e:
                logger.warning("chromadb_init_failed", error=str(e))
                return None
        return self._client

    def _get_collection(self, user_id: str):
        client = self._get_client()
        if not client:
            return None
        safe_id = user_id.replace("-", "_")
        return client.get_or_create_collection(
            name=f"{self._collection_prefix}{safe_id}",
            metadata={"hnsw:space": "cosine"},
        )

    def indexar_transacciones(self, user_id: str, transactions: list[dict]) -> int:
        """Indexa transacciones como embeddings. Retorna cantidad indexada."""
        collection = self._get_collection(user_id)
        if not collection:
            return 0

        if not transactions:
            return 0

        docs = []
        ids = []
        metadatas = []

        for txn in transactions:
            doc_text = self._txn_to_text(txn)
            doc_id = txn.get("id", f"unknown_{len(ids)}")

            docs.append(doc_text)
            ids.append(doc_id)
            metadatas.append({
                "tipo": txn.get("tipo", ""),
                "monto": float(txn.get("monto", 0)),
                "categoria": txn.get("categoria", ""),
                "fecha": txn.get("fecha", ""),
            })

        batch_size = 100
        total_indexed = 0
        for i in range(0, len(ids), batch_size):
            batch_docs = docs[i : i + batch_size]
            batch_ids = ids[i : i + batch_size]
            batch_meta = metadatas[i : i + batch_size]
            collection.upsert(
                documents=batch_docs,
                ids=batch_ids,
                metadatas=batch_meta,
            )
            total_indexed += len(batch_docs)

        logger.info(
            "transactions_indexed",
            user_id=user_id,
            count=total_indexed,
        )
        return total_indexed

    def buscar_contexto(
        self, user_id: str, query: str, top_k: int = 5
    ) -> list[dict]:
        """Busca transacciones relevantes para una query"""
        collection = self._get_collection(user_id)
        if not collection:
            return []

        try:
            count = collection.count()
            if count == 0:
                return []

            results = collection.query(
                query_texts=[query],
                n_results=min(top_k, count),
            )
        except Exception as e:
            logger.warning("chromadb_query_failed", error=str(e))
            return []

        transactions = []
        if results and results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                meta = {}
                if results["metadatas"] and results["metadatas"][0]:
                    meta = results["metadatas"][0][i]
                distance = 0
                if results["distances"] and results["distances"][0]:
                    distance = results["distances"][0][i]

                transactions.append({
                    "texto": doc,
                    "tipo": meta.get("tipo", ""),
                    "monto": meta.get("monto", 0),
                    "categoria": meta.get("categoria", ""),
                    "fecha": meta.get("fecha", ""),
                    "relevancia": round(1 - distance, 3),
                })

        return transactions

    def eliminar_usuario(self, user_id: str) -> bool:
        """Elimina la colección de un usuario"""
        client = self._get_client()
        if not client:
            return False
        safe_id = user_id.replace("-", "_")
        collection_name = f"{self._collection_prefix}{safe_id}"
        try:
            client.delete_collection(collection_name)
            return True
        except Exception:
            return False

    def _txn_to_text(self, txn: dict) -> str:
        tipo = txn.get("tipo", "transacción")
        monto = txn.get("monto", 0)
        categoria = txn.get("categoria", "general")
        fecha = txn.get("fecha", "")
        desc = txn.get("descripcion", "")

        text = f"{tipo} de ${monto:,.2f} en {categoria}"
        if fecha:
            text += f" el {fecha}"
        if desc:
            text += f" ({desc})"
        return text
