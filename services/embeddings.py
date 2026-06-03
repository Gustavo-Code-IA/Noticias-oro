import os
import sqlite3
import json
import numpy as np

try:
    import faiss
except Exception:
    faiss = None

from sentence_transformers import SentenceTransformer


class EmbeddingStore:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', data_dir: str = 'data'):
        os.makedirs(data_dir, exist_ok=True)
        self.model = SentenceTransformer(model_name)
        self.dim = self.model.get_sentence_embedding_dimension()
        self.index_path = os.path.join(data_dir, 'faiss_index.index')
        self.db_path = os.path.join(data_dir, 'embeddings.db')
        self._init_db()
        self._load_index()

    def _init_db(self):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute('''
        CREATE TABLE IF NOT EXISTS docs (
            num_id INTEGER PRIMARY KEY AUTOINCREMENT,
            doc_id TEXT UNIQUE,
            metadata TEXT
        )
        ''')
        con.commit()
        con.close()

    def _load_index(self):
        if faiss is None:
            # fallback: keep vectors in memory (simple but less efficient)
            self.index = None
            self.vectors = []
            self.ids = []
            return

        if os.path.exists(self.index_path):
            try:
                self.index = faiss.read_index(self.index_path)
            except Exception:
                # recreate empty index
                self.index = faiss.IndexIDMap(faiss.IndexFlatIP(self.dim))
        else:
            self.index = faiss.IndexIDMap(faiss.IndexFlatIP(self.dim))

    def _save_index(self):
        if faiss is None or self.index is None:
            return
        faiss.write_index(self.index, self.index_path)

    def add(self, doc_id: str, text: str, metadata: dict | None = None):
        # compute embedding
        emb = self.model.encode(text, convert_to_numpy=True)
        vec = emb.astype('float32')
        # normalize for cosine similarity using inner product
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        # insert mapping if not exists
        cur.execute('SELECT num_id FROM docs WHERE doc_id = ?', (doc_id,))
        row = cur.fetchone()
        if row:
            num_id = row[0]
            con.close()
            return num_id

        cur.execute('INSERT INTO docs (doc_id, metadata) VALUES (?,?)', (doc_id, json.dumps(metadata or {})))
        con.commit()
        num_id = cur.lastrowid
        con.close()

        if faiss is None or self.index is None:
            self.ids.append(num_id)
            self.vectors.append(vec)
        else:
            vec = np.expand_dims(vec, axis=0)
            ids = np.array([num_id], dtype='int64')
            self.index.add_with_ids(vec, ids)
            self._save_index()

        return num_id

    def query(self, text: str, top_k: int = 5):
        emb = self.model.encode(text, convert_to_numpy=True).astype('float32')
        norm = np.linalg.norm(emb)
        if norm > 0:
            emb = emb / norm

        if faiss is None or self.index is None:
            # brute-force
            if not self.vectors:
                return []
            mats = np.vstack(self.vectors)
            sims = mats.dot(emb)
            idx = np.argsort(-sims)[:top_k]
            results = []
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            for i in idx:
                num_id = self.ids[i]
                cur.execute('SELECT doc_id, metadata FROM docs WHERE num_id = ?', (num_id,))
                row = cur.fetchone()
                results.append({'doc_id': row[0], 'metadata': json.loads(row[1]), 'score': float(sims[i])})
            con.close()
            return results

        D, I = self.index.search(np.expand_dims(emb, axis=0), top_k)
        results = []
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        for score, num_id in zip(D[0], I[0]):
            if num_id == -1:
                continue
            cur.execute('SELECT doc_id, metadata FROM docs WHERE num_id = ?', (int(num_id),))
            row = cur.fetchone()
            if row:
                results.append({'doc_id': row[0], 'metadata': json.loads(row[1]), 'score': float(score)})
        con.close()
        return results


_default_store: EmbeddingStore | None = None


def get_default_store() -> EmbeddingStore:
    global _default_store
    if _default_store is None:
        _default_store = EmbeddingStore()
    return _default_store
