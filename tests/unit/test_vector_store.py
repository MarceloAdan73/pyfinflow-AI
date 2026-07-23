import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from app.ai.vector_store import ChromaDBStore


# ============================
# _txn_to_text
# ============================

def test_txn_to_text_completa():
    store = ChromaDBStore()
    txn = {
        "tipo": "Gasto",
        "monto": 15000.50,
        "categoria": "Comida",
        "fecha": "2026-07-19",
        "descripcion": "Supermercado",
    }
    result = store._txn_to_text(txn)
    assert "Gasto" in result
    assert "$15,000.50" in result
    assert "Comida" in result
    assert "2026-07-19" in result
    assert "Supermercado" in result


def test_txn_to_text_sin_descripcion():
    store = ChromaDBStore()
    txn = {
        "tipo": "Ingreso",
        "monto": 50000,
        "categoria": "Salario",
        "fecha": "2026-07-01",
    }
    result = store._txn_to_text(txn)
    assert "Ingreso" in result
    assert "$50,000" in result
    assert "Salario" in result
    assert "2026-07-01" in result
    assert "(" not in result


def test_txn_to_text_vacia():
    store = ChromaDBStore()
    result = store._txn_to_text({})
    assert "transacción" in result
    assert "$0" in result
    assert "general" in result


# ============================
# _get_client (mocked via sys.modules)
# ============================

def test_get_client_success():
    import sys
    mock_chromadb = MagicMock()
    mock_chromadb.PersistentClient.return_value = MagicMock()
    sys.modules["chromadb"] = mock_chromadb
    try:
        store = ChromaDBStore()
        store._client = None  # reset cache
        client = store._get_client()
        assert client is not None
        mock_chromadb.PersistentClient.assert_called_once()
    finally:
        del sys.modules["chromadb"]
        store._client = None


def test_get_client_import_error():
    import sys
    # Temporarily remove chromadb from sys.modules if present
    saved = sys.modules.pop("chromadb", None)
    sys.modules["chromadb"] = None  # None simulates import failure
    try:
        store = ChromaDBStore()
        store._client = None
        client = store._get_client()
        assert client is None
    finally:
        if saved is not None:
            sys.modules["chromadb"] = saved
        else:
            sys.modules.pop("chromadb", None)
        store._client = None


def test_get_client_exception():
    import sys
    mock_chromadb = MagicMock()
    mock_chromadb.PersistentClient.side_effect = Exception("Connection error")
    sys.modules["chromadb"] = mock_chromadb
    try:
        store = ChromaDBStore()
        store._client = None
        client = store._get_client()
        assert client is None
    finally:
        del sys.modules["chromadb"]
        store._client = None


# ============================
# indexar_transacciones
# ============================

@patch.object(ChromaDBStore, "_get_collection")
def test_indexar_vacio(mock_get_collection):
    store = ChromaDBStore()
    mock_collection = MagicMock()
    mock_get_collection.return_value = mock_collection

    result = store.indexar_transacciones("user_1", [])
    assert result == 0
    mock_collection.upsert.assert_not_called()


@patch.object(ChromaDBStore, "_get_collection")
def test_indexar_sin_collection(mock_get_collection):
    mock_get_collection.return_value = None
    store = ChromaDBStore()
    result = store.indexar_transacciones("user_1", [{"id": "txn_1", "tipo": "Gasto", "monto": 100}])
    assert result == 0


@patch.object(ChromaDBStore, "_get_collection")
def test_indexar_una_transaccion(mock_get_collection):
    store = ChromaDBStore()
    mock_collection = MagicMock()
    mock_get_collection.return_value = mock_collection

    txns = [{"id": "txn_1", "tipo": "Gasto", "monto": 15000, "categoria": "Comida", "fecha": "2026-07-19"}]
    result = store.indexar_transacciones("user_1", txns)
    assert result == 1
    mock_collection.upsert.assert_called_once()


@patch.object(ChromaDBStore, "_get_collection")
def test_indexar_batch(mock_get_collection):
    store = ChromaDBStore()
    mock_collection = MagicMock()
    mock_get_collection.return_value = mock_collection

    txns = [{"id": f"txn_{i}", "tipo": "Gasto", "monto": i * 1000, "categoria": "Test"} for i in range(150)]
    result = store.indexar_transacciones("user_1", txns)
    assert result == 150
    assert mock_collection.upsert.call_count == 2


# ============================
# buscar_contexto
# ============================

@patch.object(ChromaDBStore, "_get_collection")
def test_buscar_sin_collection(mock_get_collection):
    mock_get_collection.return_value = None
    store = ChromaDBStore()
    result = store.buscar_contexto("user_1", "query")
    assert result == []


@patch.object(ChromaDBStore, "_get_collection")
def test_buscar_vacio(mock_get_collection):
    store = ChromaDBStore()
    mock_collection = MagicMock()
    mock_collection.count.return_value = 0
    mock_get_collection.return_value = mock_collection

    result = store.buscar_contexto("user_1", "query")
    assert result == []


@patch.object(ChromaDBStore, "_get_collection")
def test_buscar_resultados(mock_get_collection):
    store = ChromaDBStore()
    mock_collection = MagicMock()
    mock_collection.count.return_value = 5
    mock_collection.query.return_value = {
        "documents": [["Gasto de $15,000 en Comida el 2026-07-19"]],
        "metadatas": [[{"tipo": "Gasto", "monto": 15000, "categoria": "Comida", "fecha": "2026-07-19"}]],
        "distances": [[0.2]],
    }
    mock_get_collection.return_value = mock_collection

    result = store.buscar_contexto("user_1", "comida")
    assert len(result) == 1
    assert result[0]["tipo"] == "Gasto"
    assert result[0]["relevancia"] == 0.8


@patch.object(ChromaDBStore, "_get_collection")
def test_buscar_error(mock_get_collection):
    store = ChromaDBStore()
    mock_collection = MagicMock()
    mock_collection.count.return_value = 5
    mock_collection.query.side_effect = Exception("Query failed")
    mock_get_collection.return_value = mock_collection

    result = store.buscar_contexto("user_1", "query")
    assert result == []


# ============================
# eliminar_usuario
# ============================

@patch.object(ChromaDBStore, "_get_client")
def test_eliminar_usuario_success(mock_get_client):
    store = ChromaDBStore()
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    result = store.eliminar_usuario("user_1")
    assert result is True
    mock_client.delete_collection.assert_called_once_with("txns_user_1")


@patch.object(ChromaDBStore, "_get_client")
def test_eliminar_usuario_sin_client(mock_get_client):
    mock_get_client.return_value = None
    store = ChromaDBStore()
    result = store.eliminar_usuario("user_1")
    assert result is False


@patch.object(ChromaDBStore, "_get_client")
def test_eliminar_usuario_error(mock_get_client):
    store = ChromaDBStore()
    mock_client = MagicMock()
    mock_client.delete_collection.side_effect = Exception("Not found")
    mock_get_client.return_value = mock_client

    result = store.eliminar_usuario("user_1")
    assert result is False
