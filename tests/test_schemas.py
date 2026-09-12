import pytest
from pydantic import ValidationError

from app.models.schemas import (
    Adresse,
    AttestationVente,
    Cadastre,
    Civility,
    Lot,
    MaritalStatus,
    Origine,
    Owner,
    OwnerType,
    TypeLot,
)

# ---------- Fixtures : données de base valides, réutilisables ----------

@pytest.fixture
def owner_physique_valide():
    return {
        "civility": Civility.MR,
        "first_name": "Jean",
        "last_name": "Dupont",
        "type": OwnerType.PHYSIQUE,
    }


@pytest.fixture
def owner_morale_valide():
    return {
        "civility": Civility.AUTRE,
        "first_name": "Jean",
        "last_name": "Dupont",
        "type": OwnerType.MORALE,
        "siren": "123456789",
        "entreprise_name": "SCI Les Lilas",
    }


# ---------- Owner : validateur siren (conditionnel) ----------

class TestOwnerSirenValidator:
    def test_morale_avec_siren_valide(self, owner_morale_valide):
        owner = Owner(**owner_morale_valide)
        assert owner.siren == "123456789"

    def test_morale_sans_siren_leve_erreur(self, owner_morale_valide):
        owner_morale_valide["siren"] = None
        with pytest.raises(ValidationError) as exc_info:
            Owner(**owner_morale_valide)
        assert "SIREN" in str(exc_info.value)

    def test_physique_sans_siren_est_valide(self, owner_physique_valide):
        # Pas de contrainte sur siren si type = PHYSIQUE
        owner = Owner(**owner_physique_valide)
        assert owner.siren is None


# ---------- Owner : validateur marital_status (normalisation) ----------

class TestOwnerMaritalStatusValidator:
    @pytest.mark.parametrize(
        "valeur_brute,valeur_attendue",
        [
            ("marié", MaritalStatus.MARIE),
            ("MARIÉE", MaritalStatus.MARIE),
            ("celib", MaritalStatus.CELIBATAIRE),
            ("Celibataire", MaritalStatus.CELIBATAIRE),
            ("divorcé", MaritalStatus.DIVORCE),
            ("veuve", MaritalStatus.VEUF),
        ],
    )
    def test_normalisation_variantes(self, owner_physique_valide, valeur_brute, valeur_attendue):
        owner_physique_valide["marital_status"] = valeur_brute
        owner = Owner(**owner_physique_valide)
        assert owner.marital_status == valeur_attendue

    def test_valeur_non_reconnue_renvoie_none(self, owner_physique_valide):
        # Comportement actuel du validateur : valeur inconnue -> None (pas d'erreur levée)
        owner_physique_valide["marital_status"] = "blabla"
        owner = Owner(**owner_physique_valide)
        assert owner.marital_status is None

    def test_valeur_absente_reste_none(self, owner_physique_valide):
        owner = Owner(**owner_physique_valide)
        assert owner.marital_status is None


# ---------- Owner : champs obligatoires ----------

class TestOwnerChampsObligatoires:
    def test_owner_valide_minimal(self, owner_physique_valide):
        owner = Owner(**owner_physique_valide)
        assert owner.first_name == "Jean"
        assert owner.last_name == "Dupont"

    @pytest.mark.parametrize("champ_manquant", ["civility", "first_name", "last_name", "type"])
    def test_champ_obligatoire_manquant_leve_erreur(self, owner_physique_valide, champ_manquant):
        del owner_physique_valide[champ_manquant]
        with pytest.raises(ValidationError):
            Owner(**owner_physique_valide)

    def test_civility_invalide_leve_erreur(self, owner_physique_valide):
        owner_physique_valide["civility"] = "Docteur"  # hors enum Civility
        with pytest.raises(ValidationError):
            Owner(**owner_physique_valide)


# ---------- Sous-modèles simples : Adresse, Lot, Cadastre ----------

class TestAdresse:
    def test_adresse_vide_est_valide(self):
        # Tous les champs sont Optional
        adresse = Adresse()
        assert adresse.city is None

    def test_adresse_complete(self):
        adresse = Adresse(adress="32 rue des Lilas", city="Paris", zipcode="75001")
        assert adresse.zipcode == "75001"


class TestLot:
    def test_lot_valide_minimal(self):
        lot = Lot(num_lot="12", type=TypeLot.APPARTEMENT)
        assert lot.type == TypeLot.APPARTEMENT

    def test_lot_sans_num_lot_leve_erreur(self):
        with pytest.raises(ValidationError):
            Lot(type=TypeLot.APPARTEMENT)

    def test_lot_type_invalide_leve_erreur(self):
        with pytest.raises(ValidationError):
            Lot(num_lot="12", type="Cave")  # "Cave" n'est pas dans TypeLot


class TestCadastre:
    def test_cadastre_valide(self):
        cadastre = Cadastre(prefixe="000", section="AB", num_parcelle=123)
        assert cadastre.num_parcelle == 123

    def test_cadastre_num_parcelle_mauvais_type(self):
        with pytest.raises(ValidationError):
            Cadastre(prefixe="000", section="AB", num_parcelle="pas-un-nombre")


# ---------- AttestationVente : modèle principal ----------

class TestAttestationVente:
    def test_attestation_valide_complete(self, owner_physique_valide, owner_morale_valide):
        attestation = AttestationVente(
            origin=Origine.VENTE,
            adress=Adresse(city="Paris", zipcode="75001"),
            lots=[Lot(num_lot="1", type=TypeLot.APPARTEMENT)],
            cadastres=[Cadastre(prefixe="000", section="AB", num_parcelle=42)],
            surface=65.5,
            price=350000.0,
            old_owners=[owner_morale_valide],
            new_owners=[owner_physique_valide],
        )
        assert attestation.origin == Origine.VENTE
        assert len(attestation.old_owners) == 1
        assert attestation.new_owners[0].first_name == "Jean"

    def test_attestation_sans_old_owners_leve_erreur(self, owner_physique_valide):
        with pytest.raises(ValidationError):
            AttestationVente(
                origin=Origine.VENTE,
                new_owners=[owner_physique_valide],
                # old_owners manquant volontairement
            )

    def test_attestation_sans_new_owners_leve_erreur(self, owner_physique_valide):
        with pytest.raises(ValidationError):
            AttestationVente(
                origin=Origine.VENTE,
                old_owners=[owner_physique_valide],
                # new_owners manquant volontairement
            )

    def test_attestation_origin_invalide_leve_erreur(self, owner_physique_valide):
        with pytest.raises(ValidationError):
            AttestationVente(
                origin="Location",  # hors enum Origine
                old_owners=[owner_physique_valide],
                new_owners=[owner_physique_valide],
            )

    def test_attestation_champs_optionnels_absents(self, owner_physique_valide):
        # adress, lots, cadastres, surface, price, description sont Optional
        attestation = AttestationVente(
            origin=Origine.HERITAGE,
            old_owners=[owner_physique_valide],
            new_owners=[owner_physique_valide],
        )
        assert attestation.adress is None
        assert attestation.surface is None