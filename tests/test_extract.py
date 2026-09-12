from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app
from app.models.schemas import AttestationVente, Civility, Origine, Owner, OwnerType

client = TestClient(app)


# ---------- Fixture : une attestation valide, utilisée comme réponse simulée du LLM ----------

def _attestation_exemple() -> AttestationVente:
    owner = Owner(
        civility=Civility.MR,
        first_name="Jean",
        last_name="Dupont",
        type=OwnerType.PHYSIQUE,
    )
    return AttestationVente(
        origin=Origine.VENTE,
        old_owners=[owner],
        new_owners=[owner],
    )


# ---------- Cas 1 : type de fichier invalide (avant même d'appeler OCR/LLM) ----------

def test_extract_rejette_fichier_non_pdf():
    response = client.post(
        "/extract",
        files={"file": ("document.txt", b"contenu texte", "text/plain")},
    )
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]["error"]


# ---------- Cas 2 : succès complet, OCR + LLM mockés ----------

# On patch "app.main.xxx", pas "app.services.xxx.xxx" : voir explication au-dessus.
@patch("app.main.extract_data")
@patch("app.main.extract_text_from_pdf")
def test_extract_succes(mock_ocr, mock_llm):
    mock_ocr.return_value = "Texte OCR simulé de l'attestation de vente."
    mock_llm.return_value = _attestation_exemple()

    response = client.post(
        "/extract",
        files={"file": ("attestation.pdf", b"%PDF-1.4 contenu factice", "application/pdf")},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["origin"] == "Vente"
    assert data["old_owners"][0]["first_name"] == "Jean"

    # On vérifie aussi que nos mocks ont bien été appelés une fois chacun
    mock_ocr.assert_called_once()
    mock_llm.assert_called_once_with("Texte OCR simulé de l'attestation de vente.")


# ---------- Cas 3 : l'OCR ne renvoie rien d'exploitable ----------

@patch("app.main.extract_data")
@patch("app.main.extract_text_from_pdf")
def test_extract_ocr_vide(mock_ocr, mock_llm):
    mock_ocr.return_value = ""

    response = client.post(
        "/extract",
        files={"file": ("attestation.pdf", b"%PDF-1.4 contenu factice", "application/pdf")},
    )

    assert response.status_code == 400
    assert "Unable to extract text" in response.json()["detail"]["error"]
    # Le LLM ne doit jamais être appelé si l'OCR échoue
    mock_llm.assert_not_called()


# ---------- Cas 4 : le LLM/validation échoue après les retries (ValueError) ----------

@patch("app.main.extract_data")
@patch("app.main.extract_text_from_pdf")
def test_extract_llm_echoue_apres_retries(mock_ocr, mock_llm):
    mock_ocr.return_value = "Texte OCR simulé."
    mock_llm.side_effect = ValueError(
        {"error": "Unable to validate extracted data after all retries.", "details": "..."}
    )

    response = client.post(
        "/extract",
        files={"file": ("attestation.pdf", b"%PDF-1.4 contenu factice", "application/pdf")},
    )

    assert response.status_code == 422