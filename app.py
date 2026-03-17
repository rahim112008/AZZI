import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, datetime, timedelta
import json
import os

# ─── Configuration ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="BTP Manager Pro",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Styles ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main-title {
    font-size: 2.2rem; font-weight: 700; color: #1a1a2e;
    border-left: 6px solid #e94560; padding-left: 16px; margin-bottom: 8px;
}
.section-card {
    background: #f8f9fb; border-radius: 12px; padding: 20px;
    border: 1px solid #e2e8f0; margin-bottom: 16px;
}
.kpi-box {
    background: linear-gradient(135deg, #1a1a2e, #16213e);
    color: white; border-radius: 12px; padding: 20px; text-align: center;
}
.kpi-value { font-size: 2rem; font-weight: 700; color: #e94560; }
.kpi-label { font-size: 0.85rem; opacity: 0.8; margin-top: 4px; }
.badge-green  { background:#d1fae5; color:#065f46; padding:3px 10px; border-radius:20px; font-size:0.8rem; }
.badge-orange { background:#fed7aa; color:#9a3412; padding:3px 10px; border-radius:20px; font-size:0.8rem; }
.badge-red    { background:#fee2e2; color:#991b1b; padding:3px 10px; border-radius:20px; font-size:0.8rem; }
.badge-blue   { background:#dbeafe; color:#1e40af; padding:3px 10px; border-radius:20px; font-size:0.8rem; }
</style>
""", unsafe_allow_html=True)

# ─── Data persistence helpers ─────────────────────────────────────────────────
DATA_FILE = "btp_data.json"

def load_data():
    default = {
        "projets": [],
        "employes": [],
        "assurances": [],
        "depenses": [],
        "cahiers_charge": [],
        "impots": [],
        "transactions_financieres": [],
        "creances": [],
        "fournisseurs": [],
        "materiaux": [],
    }
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
            for k in default:
                if k not in saved:
                    saved[k] = default[k]
            return saved
    return default

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)

if "data" not in st.session_state:
    st.session_state.data = load_data()

def save():
    save_data(st.session_state.data)

# ─── Sidebar navigation ───────────────────────────────────────────────────────
st.sidebar.markdown("## 🏗️ BTP Manager Pro")
st.sidebar.markdown("---")
PAGES = {
    "📊 Tableau de bord":       "dashboard",
    "📁 Projets":               "projets",
    "👷 Employés & Ouvriers":   "employes",
    "🛡️ Assurances":            "assurances",
    "💸 Dépenses":              "depenses",
    "📋 Cahiers des charges":   "cahiers",
    "🧾 Impôts & Taxes":        "impots",
    "💰 Finances":              "finances",
    "🤝 Créances (Dettes envers moi)": "creances",
    "🏭 Fournisseurs":          "fournisseurs",
    "🧱 Matériaux & Stock":     "materiaux",
    "📤 Export des données":    "export",
}
page_choice = st.sidebar.radio("Navigation", list(PAGES.keys()))
page = PAGES[page_choice]

st.sidebar.markdown("---")
st.sidebar.caption("© 2025 BTP Manager Pro")

# ══════════════════════════════════════════════════════════════════════════════
# 1.  TABLEAU DE BORD
# ══════════════════════════════════════════════════════════════════════════════
if page == "dashboard":
    st.markdown('<p class="main-title">📊 Tableau de bord</p>', unsafe_allow_html=True)

    data = st.session_state.data
    projets   = data["projets"]
    employes  = data["employes"]
    depenses  = data["depenses"]
    creances  = data["creances"]
    finances  = data["transactions_financieres"]

    # KPIs
    nb_projets   = len(projets)
    nb_employes  = len(employes)
    total_dep    = sum(float(d.get("montant", 0)) for d in depenses)
    total_crean  = sum(float(c.get("montant", 0)) for c in creances if c.get("statut") != "Payé")
    revenus      = sum(float(t.get("montant", 0)) for t in finances if t.get("type") == "Recette")
    charges      = sum(float(t.get("montant", 0)) for t in finances if t.get("type") == "Charge")
    solde        = revenus - charges

    c1, c2, c3, c4 = st.columns(4)
    for col, val, lab in [
        (c1, nb_projets,        "Projets"),
        (c2, nb_employes,       "Employés"),
        (c3, f"{solde:,.0f} DA", "Solde financier"),
        (c4, f"{total_crean:,.0f} DA", "Créances en cours"),
    ]:
        col.markdown(f"""
        <div class="kpi-box">
            <div class="kpi-value">{val}</div>
            <div class="kpi-label">{lab}</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    col_a, col_b = st.columns(2)

    # Projets par statut
    with col_a:
        st.subheader("📁 Statut des projets")
        if projets:
            statuts = {}
            for p in projets:
                s = p.get("statut", "Inconnu")
                statuts[s] = statuts.get(s, 0) + 1
            fig = px.pie(values=list(statuts.values()), names=list(statuts.keys()),
                         color_discrete_sequence=["#e94560","#1a1a2e","#f5a623","#4caf50","#2196f3"])
            fig.update_layout(margin=dict(t=10,b=10,l=10,r=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucun projet enregistré.")

    # Dépenses par catégorie
    with col_b:
        st.subheader("💸 Dépenses par catégorie")
        if depenses:
            cats = {}
            for d in depenses:
                c = d.get("categorie", "Autre")
                cats[c] = cats.get(c, 0) + float(d.get("montant", 0))
            fig2 = px.bar(x=list(cats.keys()), y=list(cats.values()),
                          labels={"x": "Catégorie", "y": "DA"},
                          color=list(cats.keys()),
                          color_discrete_sequence=px.colors.qualitative.Set2)
            fig2.update_layout(margin=dict(t=10,b=10,l=10,r=10), showlegend=False)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Aucune dépense enregistrée.")

    # Timeline projets
    st.subheader("📅 Calendrier des projets")
    if projets:
        rows = []
        for p in projets:
            if p.get("date_debut") and p.get("date_fin"):
                rows.append(dict(
                    Projet=p["nom"],
                    Début=p["date_debut"],
                    Fin=p["date_fin"],
                    Statut=p.get("statut", "En cours"),
                ))
        if rows:
            df_g = pd.DataFrame(rows)
            fig3 = px.timeline(df_g, x_start="Début", x_end="Fin", y="Projet", color="Statut",
                               color_discrete_map={"En cours":"#2196f3","Terminé":"#4caf50",
                                                   "En attente":"#f5a623","Annulé":"#e94560"})
            fig3.update_layout(margin=dict(t=10,b=10,l=10,r=10))
            st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Aucun projet avec des dates.")

    # Projets qui se terminent bientôt
    st.subheader("⚠️ Projets se terminant dans les 30 jours")
    today = date.today()
    alertes = [p for p in projets
               if p.get("date_fin") and p.get("statut") not in ("Terminé","Annulé")
               and 0 <= (date.fromisoformat(p["date_fin"]) - today).days <= 30]
    if alertes:
        for p in alertes:
            j_rest = (date.fromisoformat(p["date_fin"]) - today).days
            st.warning(f"🔔 **{p['nom']}** — se termine dans **{j_rest} jour(s)** ({p['date_fin']})")
    else:
        st.success("Aucune échéance imminente.")

# ══════════════════════════════════════════════════════════════════════════════
# 2.  PROJETS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "projets":
    st.markdown('<p class="main-title">📁 Gestion des Projets</p>', unsafe_allow_html=True)
    data = st.session_state.data

    tab1, tab2 = st.tabs(["➕ Nouveau projet", "📋 Liste des projets"])

    with tab1:
        with st.form("form_projet"):
            c1, c2 = st.columns(2)
            nom         = c1.text_input("Nom du projet *")
            client      = c2.text_input("Maître d'ouvrage (client) *")
            c3, c4      = st.columns(2)
            lieu        = c3.text_input("Lieu / Wilaya")
            type_trav   = c4.selectbox("Type de travaux",
                ["Bâtiment", "Route / VRD", "Hydraulique", "Électricité", "Terrassement", "Autre"])
            c5, c6      = st.columns(2)
            date_debut  = c5.date_input("Date de début")
            date_fin    = c6.date_input("Date de fin prévue")
            c7, c8      = st.columns(2)
            budget      = c7.number_input("Budget (DA)", min_value=0.0, step=10000.0)
            statut      = c8.selectbox("Statut", ["En attente","En cours","Terminé","Annulé","Suspendu"])
            description = st.text_area("Description / Notes")
            num_marche  = st.text_input("Numéro de marché / référence")
            submitted   = st.form_submit_button("💾 Enregistrer le projet", use_container_width=True)

        if submitted:
            if not nom or not client:
                st.error("Nom et client sont obligatoires.")
            else:
                data["projets"].append({
                    "id": len(data["projets"]) + 1,
                    "nom": nom, "client": client, "lieu": lieu,
                    "type": type_trav, "date_debut": str(date_debut),
                    "date_fin": str(date_fin), "budget": budget,
                    "statut": statut, "description": description,
                    "num_marche": num_marche,
                    "date_creation": str(date.today()),
                })
                save()
                st.success(f"✅ Projet « {nom} » enregistré !")

    with tab2:
        projets = data["projets"]
        if not projets:
            st.info("Aucun projet enregistré pour l'instant.")
        else:
            filtre = st.selectbox("Filtrer par statut", ["Tous","En cours","En attente","Terminé","Annulé","Suspendu"])
            liste = projets if filtre == "Tous" else [p for p in projets if p.get("statut") == filtre]
            for i, p in enumerate(liste):
                badge_color = {"En cours":"badge-blue","Terminé":"badge-green",
                               "En attente":"badge-orange","Annulé":"badge-red",
                               "Suspendu":"badge-orange"}.get(p.get("statut",""), "badge-blue")
                with st.expander(f"🏗️  {p['nom']}  —  {p.get('client','')}"):
                    col1, col2, col3 = st.columns(3)
                    col1.markdown(f"**Lieu :** {p.get('lieu','—')}")
                    col2.markdown(f"**Type :** {p.get('type','—')}")
                    col3.markdown(f"**Budget :** {float(p.get('budget',0)):,.0f} DA")
                    col1.markdown(f"**Début :** {p.get('date_debut','—')}")
                    col2.markdown(f"**Fin :** {p.get('date_fin','—')}")
                    col3.markdown(f"**N° marché :** {p.get('num_marche','—')}")
                    st.markdown(f"**Statut :** <span class='{badge_color}'>{p.get('statut','')}</span>", unsafe_allow_html=True)
                    if p.get("description"):
                        st.markdown(f"**Notes :** {p['description']}")
                    # Modifier statut rapide
                    nouveau_statut = st.selectbox("Changer statut", ["En attente","En cours","Terminé","Annulé","Suspendu"],
                                                  index=["En attente","En cours","Terminé","Annulé","Suspendu"].index(p.get("statut","En cours")),
                                                  key=f"stat_{i}")
                    if st.button("Mettre à jour", key=f"upd_{i}"):
                        idx = data["projets"].index(p)
                        data["projets"][idx]["statut"] = nouveau_statut
                        save()
                        st.rerun()
                    if st.button("🗑️ Supprimer ce projet", key=f"del_proj_{i}"):
                        data["projets"].remove(p)
                        save()
                        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# 3.  EMPLOYÉS & OUVRIERS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "employes":
    st.markdown('<p class="main-title">👷 Employés & Ouvriers</p>', unsafe_allow_html=True)
    data = st.session_state.data

    tab1, tab2 = st.tabs(["➕ Ajouter", "📋 Liste"])

    with tab1:
        with st.form("form_emp"):
            c1, c2 = st.columns(2)
            nom_emp    = c1.text_input("Nom & Prénom *")
            poste      = c2.selectbox("Poste / Fonction",
                ["Conducteur de travaux","Chef de chantier","Technicien",
                 "Maçon","Électricien","Plombier","Soudeur","Chauffeur",
                 "Ouvrier qualifié","Manœuvre","Ingénieur","Comptable","Secrétaire","Autre"])
            c3, c4     = st.columns(2)
            telephone  = c3.text_input("Téléphone")
            adresse    = c4.text_input("Adresse")
            c5, c6     = st.columns(2)
            date_embauche = c5.date_input("Date d'embauche")
            salaire    = c6.number_input("Salaire mensuel (DA)", min_value=0.0, step=500.0)
            c7, c8     = st.columns(2)
            type_contrat = c7.selectbox("Type de contrat", ["CDI","CDD","Journalier","Intérim","Sous-traitant"])
            num_securite = c8.text_input("N° Sécurité sociale / NAS")
            projet_aff  = st.selectbox("Affecté au projet",
                ["—"] + [p["nom"] for p in data["projets"]])
            note_emp    = st.text_area("Notes")
            sub_emp     = st.form_submit_button("💾 Enregistrer l'employé", use_container_width=True)

        if sub_emp:
            if not nom_emp:
                st.error("Le nom est obligatoire.")
            else:
                data["employes"].append({
                    "id": len(data["employes"]) + 1,
                    "nom": nom_emp, "poste": poste, "telephone": telephone,
                    "adresse": adresse, "date_embauche": str(date_embauche),
                    "salaire": salaire, "type_contrat": type_contrat,
                    "num_securite": num_securite, "projet": projet_aff,
                    "notes": note_emp, "actif": True,
                })
                save()
                st.success(f"✅ Employé « {nom_emp} » enregistré !")

    with tab2:
        employes = data["employes"]
        if not employes:
            st.info("Aucun employé enregistré.")
        else:
            df = pd.DataFrame(employes)[["nom","poste","type_contrat","salaire","projet","date_embauche"]]
            df.columns = ["Nom","Poste","Contrat","Salaire (DA)","Projet","Date embauche"]
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.markdown(f"**Total masse salariale mensuelle : {sum(float(e.get('salaire',0)) for e in employes):,.0f} DA**")

            # Supprimer
            noms = [e["nom"] for e in employes]
            to_del = st.selectbox("Supprimer un employé", ["—"] + noms)
            if st.button("🗑️ Supprimer") and to_del != "—":
                data["employes"] = [e for e in employes if e["nom"] != to_del]
                save()
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# 4.  ASSURANCES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "assurances":
    st.markdown('<p class="main-title">🛡️ Assurances des Travailleurs & Chantiers</p>', unsafe_allow_html=True)
    data = st.session_state.data

    tab1, tab2 = st.tabs(["➕ Ajouter", "📋 Liste"])

    with tab1:
        with st.form("form_ass"):
            c1, c2 = st.columns(2)
            type_ass    = c1.selectbox("Type d'assurance",
                ["Assurance travailleur (AT/MP)","Responsabilité civile",
                 "Tous risques chantier (TRC)","Assurance matériel",
                 "Assurance décennale","Mutuelle employés","Autre"])
            assureur    = c2.text_input("Compagnie d'assurance *")
            c3, c4      = st.columns(2)
            num_police  = c3.text_input("Numéro de police")
            concerne    = c4.text_input("Concerne (employé / projet / matériel)")
            c5, c6      = st.columns(2)
            date_debut_a = c5.date_input("Date de début")
            date_fin_a   = c6.date_input("Date d'expiration")
            c7, c8      = st.columns(2)
            prime       = c7.number_input("Prime annuelle (DA)", min_value=0.0, step=1000.0)
            statut_ass  = c8.selectbox("Statut", ["Active","Expirée","En renouvellement"])
            notes_ass   = st.text_area("Notes")
            sub_ass     = st.form_submit_button("💾 Enregistrer l'assurance", use_container_width=True)

        if sub_ass:
            if not assureur:
                st.error("La compagnie est obligatoire.")
            else:
                data["assurances"].append({
                    "type": type_ass, "assureur": assureur,
                    "num_police": num_police, "concerne": concerne,
                    "date_debut": str(date_debut_a), "date_fin": str(date_fin_a),
                    "prime": prime, "statut": statut_ass, "notes": notes_ass,
                })
                save()
                st.success("✅ Assurance enregistrée !")

    with tab2:
        assurances = data["assurances"]
        if not assurances:
            st.info("Aucune assurance enregistrée.")
        else:
            today = date.today()
            for a in assurances:
                exp = date.fromisoformat(a["date_fin"]) if a.get("date_fin") else None
                jours_rest = (exp - today).days if exp else None
                alert = ""
                if jours_rest is not None and jours_rest <= 30:
                    alert = f"⚠️ Expire dans {jours_rest}j"
                with st.expander(f"🛡️ {a['type']} — {a['assureur']} {alert}"):
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"**Police :** {a.get('num_police','—')}")
                    c2.markdown(f"**Concerne :** {a.get('concerne','—')}")
                    c3.markdown(f"**Prime :** {float(a.get('prime',0)):,.0f} DA/an")
                    c1.markdown(f"**Début :** {a.get('date_debut','—')}")
                    c2.markdown(f"**Expiration :** {a.get('date_fin','—')}")
                    c3.markdown(f"**Statut :** {a.get('statut','—')}")
                    if jours_rest is not None and jours_rest <= 30:
                        st.warning(f"⚠️ Cette assurance expire dans **{jours_rest} jour(s)** — pensez à la renouveler !")

# ══════════════════════════════════════════════════════════════════════════════
# 5.  DÉPENSES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "depenses":
    st.markdown('<p class="main-title">💸 Gestion des Dépenses</p>', unsafe_allow_html=True)
    data = st.session_state.data

    tab1, tab2, tab3 = st.tabs(["➕ Ajouter", "📋 Liste", "📊 Analyse"])

    with tab1:
        with st.form("form_dep"):
            c1, c2 = st.columns(2)
            libelle   = c1.text_input("Libellé de la dépense *")
            categorie = c2.selectbox("Catégorie",
                ["Main d'œuvre","Matériaux","Matériel / Location",
                 "Transport","Sous-traitance","Carburant","Alimentation chantier",
                 "Frais administratifs","Assurance","Impôts / Taxes","Autre"])
            c3, c4    = st.columns(2)
            montant   = c3.number_input("Montant (DA) *", min_value=0.0, step=100.0)
            date_dep  = c4.date_input("Date de la dépense")
            c5, c6    = st.columns(2)
            projet_dep = c5.selectbox("Projet concerné",
                ["—"] + [p["nom"] for p in data["projets"]])
            mode_paiement = c6.selectbox("Mode de paiement",
                ["Espèces","Virement bancaire","Chèque","Carte","Autre"])
            fournisseur_dep = st.text_input("Fournisseur / Bénéficiaire")
            ref_facture = st.text_input("Référence facture / bon de commande")
            notes_dep = st.text_area("Notes")
            sub_dep = st.form_submit_button("💾 Enregistrer la dépense", use_container_width=True)

        if sub_dep:
            if not libelle or montant <= 0:
                st.error("Libellé et montant sont obligatoires.")
            else:
                data["depenses"].append({
                    "libelle": libelle, "categorie": categorie,
                    "montant": montant, "date": str(date_dep),
                    "projet": projet_dep, "mode_paiement": mode_paiement,
                    "fournisseur": fournisseur_dep,
                    "ref_facture": ref_facture, "notes": notes_dep,
                })
                save()
                st.success(f"✅ Dépense « {libelle} » de {montant:,.0f} DA enregistrée !")

    with tab2:
        depenses = data["depenses"]
        if not depenses:
            st.info("Aucune dépense enregistrée.")
        else:
            filtre_proj = st.selectbox("Filtrer par projet",
                ["Tous"] + [p["nom"] for p in data["projets"]])
            liste_dep = depenses if filtre_proj == "Tous" \
                else [d for d in depenses if d.get("projet") == filtre_proj]
            df_dep = pd.DataFrame(liste_dep)[["date","libelle","categorie","montant","projet","mode_paiement","fournisseur"]]
            df_dep.columns = ["Date","Libellé","Catégorie","Montant (DA)","Projet","Paiement","Fournisseur"]
            df_dep = df_dep.sort_values("Date", ascending=False)
            st.dataframe(df_dep, use_container_width=True, hide_index=True)
            st.markdown(f"**Total : {sum(float(d.get('montant',0)) for d in liste_dep):,.0f} DA**")

    with tab3:
        depenses = data["depenses"]
        if depenses:
            df_a = pd.DataFrame(depenses)
            df_a["montant"] = df_a["montant"].astype(float)
            df_a["date"] = pd.to_datetime(df_a["date"])
            df_a["mois"] = df_a["date"].dt.to_period("M").astype(str)

            fig = px.bar(df_a.groupby("categorie")["montant"].sum().reset_index(),
                         x="categorie", y="montant", title="Dépenses par catégorie",
                         color="categorie")
            st.plotly_chart(fig, use_container_width=True)

            fig2 = px.line(df_a.groupby("mois")["montant"].sum().reset_index(),
                           x="mois", y="montant", title="Évolution mensuelle des dépenses",
                           markers=True)
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Pas de données pour l'analyse.")

# ══════════════════════════════════════════════════════════════════════════════
# 6.  CAHIERS DES CHARGES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "cahiers":
    st.markdown('<p class="main-title">📋 Cahiers des Charges</p>', unsafe_allow_html=True)
    data = st.session_state.data

    tab1, tab2 = st.tabs(["➕ Ajouter", "📋 Liste"])

    with tab1:
        with st.form("form_cdc"):
            c1, c2 = st.columns(2)
            titre_cdc  = c1.text_input("Titre du cahier des charges *")
            projet_cdc = c2.selectbox("Projet lié",
                ["—"] + [p["nom"] for p in data["projets"]])
            c3, c4     = st.columns(2)
            ref_cdc    = c3.text_input("Référence / Numéro")
            date_cdc   = c4.date_input("Date d'émission")
            c5, c6     = st.columns(2)
            maitre_ouv = c5.text_input("Maître d'ouvrage")
            maitre_oeuvre = c6.text_input("Maître d'œuvre")
            type_cdc   = st.selectbox("Type",
                ["CCTP (Technique)","CCAP (Administratif)","CCTG (Général)","Devis quantitatif","Autre"])
            objet      = st.text_area("Objet des travaux")
            exigences  = st.text_area("Exigences techniques principales")
            delai      = st.number_input("Délai d'exécution (jours)", min_value=0, step=1)
            penalites  = st.text_input("Pénalités de retard")
            montant_cdc = st.number_input("Montant estimé (DA)", min_value=0.0, step=10000.0)
            statut_cdc  = st.selectbox("Statut",
                ["En préparation","Soumis","Approuvé","En cours d'exécution","Clôturé","Litigieux"])
            sub_cdc    = st.form_submit_button("💾 Enregistrer", use_container_width=True)

        if sub_cdc:
            if not titre_cdc:
                st.error("Le titre est obligatoire.")
            else:
                data["cahiers_charge"].append({
                    "titre": titre_cdc, "projet": projet_cdc,
                    "ref": ref_cdc, "date": str(date_cdc),
                    "maitre_ouv": maitre_ouv, "maitre_oeuvre": maitre_oeuvre,
                    "type": type_cdc, "objet": objet,
                    "exigences": exigences, "delai": delai,
                    "penalites": penalites, "montant": montant_cdc,
                    "statut": statut_cdc,
                })
                save()
                st.success(f"✅ Cahier des charges « {titre_cdc} » enregistré !")

    with tab2:
        cahiers = data["cahiers_charge"]
        if not cahiers:
            st.info("Aucun cahier des charges enregistré.")
        else:
            for cdc in cahiers:
                with st.expander(f"📋 {cdc['titre']} — {cdc.get('statut','')}"):
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"**Projet :** {cdc.get('projet','—')}")
                    c2.markdown(f"**Réf :** {cdc.get('ref','—')}")
                    c3.markdown(f"**Date :** {cdc.get('date','—')}")
                    c1.markdown(f"**Type :** {cdc.get('type','—')}")
                    c2.markdown(f"**Délai :** {cdc.get('delai','—')} jours")
                    c3.markdown(f"**Montant :** {float(cdc.get('montant',0)):,.0f} DA")
                    if cdc.get("objet"):
                        st.markdown(f"**Objet :** {cdc['objet']}")
                    if cdc.get("exigences"):
                        st.markdown(f"**Exigences :** {cdc['exigences']}")
                    if cdc.get("penalites"):
                        st.markdown(f"**Pénalités :** {cdc['penalites']}")

# ══════════════════════════════════════════════════════════════════════════════
# 7.  IMPÔTS & TAXES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "impots":
    st.markdown('<p class="main-title">🧾 Impôts & Taxes</p>', unsafe_allow_html=True)
    data = st.session_state.data

    tab1, tab2 = st.tabs(["➕ Ajouter", "📋 Liste"])

    with tab1:
        with st.form("form_imp"):
            c1, c2 = st.columns(2)
            type_imp  = c1.selectbox("Type d'impôt / taxe",
                ["IRG (Impôt sur le revenu global)",
                 "IBS (Impôt sur les bénéfices des sociétés)",
                 "TAP (Taxe sur l'activité professionnelle)",
                 "TVA (Taxe sur la valeur ajoutée)",
                 "Taxe foncière","Cotisations CNAS","Cotisations CASNOS",
                 "Patente","Taxe d'apprentissage","Taxe de formation professionnelle","Autre"])
            periode   = c2.text_input("Période (ex: T1 2025, Année 2024)")
            c3, c4    = st.columns(2)
            montant_imp = c3.number_input("Montant dû (DA)", min_value=0.0, step=100.0)
            date_echeance = c4.date_input("Date d'échéance")
            c5, c6    = st.columns(2)
            date_paiement_imp = c5.date_input("Date de paiement (si payé)", value=None)
            statut_imp = c6.selectbox("Statut", ["À payer","Payé","En retard","Contesté"])
            ref_quittance = st.text_input("Référence quittance / reçu")
            notes_imp  = st.text_area("Notes")
            sub_imp    = st.form_submit_button("💾 Enregistrer", use_container_width=True)

        if sub_imp:
            data["impots"].append({
                "type": type_imp, "periode": periode,
                "montant": montant_imp,
                "date_echeance": str(date_echeance),
                "date_paiement": str(date_paiement_imp) if date_paiement_imp else "",
                "statut": statut_imp,
                "ref_quittance": ref_quittance, "notes": notes_imp,
            })
            save()
            st.success("✅ Impôt / taxe enregistré !")

    with tab2:
        impots = data["impots"]
        if not impots:
            st.info("Aucun impôt enregistré.")
        else:
            total_du = sum(float(i.get("montant",0)) for i in impots if i.get("statut") != "Payé")
            st.metric("Total impôts à payer", f"{total_du:,.0f} DA")
            df_imp = pd.DataFrame(impots)[["type","periode","montant","date_echeance","statut","ref_quittance"]]
            df_imp.columns = ["Type","Période","Montant (DA)","Échéance","Statut","Réf. quittance"]
            st.dataframe(df_imp, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# 8.  FINANCES
# ══════════════════════════════════════════════════════════════════════════════
elif page == "finances":
    st.markdown('<p class="main-title">💰 Gestion Financière</p>', unsafe_allow_html=True)
    data = st.session_state.data

    tab1, tab2, tab3 = st.tabs(["➕ Transaction", "📋 Historique", "📊 Bilan"])

    with tab1:
        with st.form("form_fin"):
            c1, c2 = st.columns(2)
            type_trans = c1.selectbox("Type", ["Recette","Charge","Virement interne"])
            libelle_f  = c2.text_input("Libellé *")
            c3, c4     = st.columns(2)
            montant_f  = c3.number_input("Montant (DA) *", min_value=0.0, step=100.0)
            date_f     = c4.date_input("Date")
            c5, c6     = st.columns(2)
            categorie_f = c5.selectbox("Catégorie",
                ["Règlement client","Avance sur marché","Retenue de garantie libérée",
                 "Salaires","Fournisseur","Sous-traitant","Impôts","Assurance",
                 "Matériel","Frais généraux","Autre"])
            projet_f   = c6.selectbox("Projet",
                ["—"] + [p["nom"] for p in data["projets"]])
            mode_f     = st.selectbox("Mode de paiement",
                ["Virement","Chèque","Espèces","Prélèvement","Autre"])
            notes_f    = st.text_area("Notes")
            sub_fin    = st.form_submit_button("💾 Enregistrer la transaction", use_container_width=True)

        if sub_fin:
            if not libelle_f or montant_f <= 0:
                st.error("Libellé et montant obligatoires.")
            else:
                data["transactions_financieres"].append({
                    "type": type_trans, "libelle": libelle_f,
                    "montant": montant_f, "date": str(date_f),
                    "categorie": categorie_f, "projet": projet_f,
                    "mode": mode_f, "notes": notes_f,
                })
                save()
                st.success("✅ Transaction enregistrée !")

    with tab2:
        transactions = data["transactions_financieres"]
        if not transactions:
            st.info("Aucune transaction.")
        else:
            df_fin = pd.DataFrame(transactions)
            df_fin["montant"] = df_fin["montant"].astype(float)
            df_fin = df_fin.sort_values("date", ascending=False)
            df_fin["Signe"] = df_fin["type"].map({"Recette":"+","Charge":"−","Virement interne":"↔"})
            st.dataframe(df_fin[["date","type","libelle","montant","categorie","projet","mode"]],
                         use_container_width=True, hide_index=True)

    with tab3:
        transactions = data["transactions_financieres"]
        if transactions:
            df_b = pd.DataFrame(transactions)
            df_b["montant"] = df_b["montant"].astype(float)
            revenus = df_b[df_b["type"]=="Recette"]["montant"].sum()
            charges = df_b[df_b["type"]=="Charge"]["montant"].sum()
            solde   = revenus - charges

            c1, c2, c3 = st.columns(3)
            c1.metric("Total recettes", f"{revenus:,.0f} DA")
            c2.metric("Total charges",  f"{charges:,.0f} DA")
            c3.metric("Solde net",       f"{solde:,.0f} DA",
                       delta=f"{solde:,.0f}" if solde >= 0 else f"{solde:,.0f}")

            fig = go.Figure(go.Waterfall(
                name="Bilan",
                orientation="v",
                measure=["relative","relative","total"],
                x=["Recettes","Charges","Solde"],
                y=[revenus, -charges, 0],
                connector={"line": {"color": "rgb(63,63,63)"}},
                increasing={"marker": {"color": "#4caf50"}},
                decreasing={"marker": {"color": "#e94560"}},
                totals={"marker": {"color": "#2196f3"}},
            ))
            fig.update_layout(title="Waterfall financier", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

            # Par projet
            st.subheader("Recettes vs Charges par projet")
            grp = df_b.groupby(["projet","type"])["montant"].sum().reset_index()
            fig2 = px.bar(grp, x="projet", y="montant", color="type", barmode="group",
                          color_discrete_map={"Recette":"#4caf50","Charge":"#e94560"})
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Pas encore de transactions.")

# ══════════════════════════════════════════════════════════════════════════════
# 9.  CRÉANCES (GENS QUI ME DOIVENT DE L'ARGENT)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "creances":
    st.markdown('<p class="main-title">🤝 Créances — Personnes qui me doivent de l'argent</p>', unsafe_allow_html=True)
    data = st.session_state.data

    tab1, tab2 = st.tabs(["➕ Ajouter une créance", "📋 Liste"])

    with tab1:
        with st.form("form_crean"):
            c1, c2 = st.columns(2)
            debiteur   = c1.text_input("Nom du débiteur *")
            type_crean = c2.selectbox("Type",
                ["Client (règlement partiel)","Avance non remboursée",
                 "Retenue de garantie","Prêt à un employé","Sous-traitant","Autre"])
            c3, c4     = st.columns(2)
            montant_cr = c3.number_input("Montant dû (DA) *", min_value=0.0, step=1000.0)
            montant_r  = c4.number_input("Montant déjà reçu (DA)", min_value=0.0, step=100.0)
            c5, c6     = st.columns(2)
            date_echeance_cr = c5.date_input("Date d'échéance prévue")
            projet_cr  = c6.selectbox("Projet lié",
                ["—"] + [p["nom"] for p in data["projets"]])
            description_cr = st.text_area("Description / Contexte")
            statut_cr  = st.selectbox("Statut", ["En cours","Partiellement payé","Payé","Litigieux","Irrécouvrable"])
            contact_cr = st.text_input("Coordonnées du débiteur (tél / adresse)")
            sub_cr     = st.form_submit_button("💾 Enregistrer", use_container_width=True)

        if sub_cr:
            if not debiteur or montant_cr <= 0:
                st.error("Débiteur et montant obligatoires.")
            else:
                data["creances"].append({
                    "debiteur": debiteur, "type": type_crean,
                    "montant": montant_cr, "montant_recu": montant_r,
                    "date_echeance": str(date_echeance_cr),
                    "projet": projet_cr, "description": description_cr,
                    "statut": statut_cr, "contact": contact_cr,
                    "date_creation": str(date.today()),
                })
                save()
                st.success(f"✅ Créance sur « {debiteur} » enregistrée !")

    with tab2:
        creances = data["creances"]
        if not creances:
            st.info("Aucune créance enregistrée.")
        else:
            total_du = sum(float(c.get("montant",0)) - float(c.get("montant_recu",0))
                          for c in creances if c.get("statut") not in ("Payé","Irrécouvrable"))
            st.metric("💰 Total créances en cours", f"{total_du:,.0f} DA")

            for i, cr in enumerate(creances):
                reste = float(cr.get("montant",0)) - float(cr.get("montant_recu",0))
                badge_map = {"En cours":"badge-orange","Partiellement payé":"badge-blue",
                             "Payé":"badge-green","Litigieux":"badge-red","Irrécouvrable":"badge-red"}
                badge = badge_map.get(cr.get("statut",""), "badge-orange")
                with st.expander(f"💳 {cr['debiteur']} — Reste : {reste:,.0f} DA"):
                    c1, c2, c3 = st.columns(3)
                    c1.markdown(f"**Type :** {cr.get('type','—')}")
                    c2.markdown(f"**Montant total :** {float(cr.get('montant',0)):,.0f} DA")
                    c3.markdown(f"**Reçu :** {float(cr.get('montant_recu',0)):,.0f} DA")
                    c1.markdown(f"**Échéance :** {cr.get('date_echeance','—')}")
                    c2.markdown(f"**Projet :** {cr.get('projet','—')}")
                    c3.markdown(f"**Contact :** {cr.get('contact','—')}")
                    st.markdown(f"**Statut :** <span class='{badge}'>{cr.get('statut','')}</span>", unsafe_allow_html=True)
                    if cr.get("description"):
                        st.markdown(f"**Notes :** {cr['description']}")

                    # Enregistrer un paiement partiel
                    paiement_partiel = st.number_input("Enregistrer paiement reçu (DA)",
                                                       min_value=0.0, step=100.0, key=f"pay_cr_{i}")
                    if st.button("✅ Valider paiement", key=f"val_cr_{i}") and paiement_partiel > 0:
                        idx = data["creances"].index(cr)
                        data["creances"][idx]["montant_recu"] = float(cr.get("montant_recu",0)) + paiement_partiel
                        nouveau_reste = float(data["creances"][idx]["montant"]) - float(data["creances"][idx]["montant_recu"])
                        if nouveau_reste <= 0:
                            data["creances"][idx]["statut"] = "Payé"
                        save()
                        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# 10.  FOURNISSEURS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "fournisseurs":
    st.markdown('<p class="main-title">🏭 Fournisseurs</p>', unsafe_allow_html=True)
    data = st.session_state.data

    tab1, tab2 = st.tabs(["➕ Ajouter", "📋 Liste"])

    with tab1:
        with st.form("form_four"):
            c1, c2 = st.columns(2)
            nom_four   = c1.text_input("Nom du fournisseur *")
            type_four  = c2.selectbox("Catégorie",
                ["Matériaux de construction","Matériel / Outillage","Location engin",
                 "Carburant","Quincaillerie","Électricité","Plomberie","Transport","Autre"])
            c3, c4     = st.columns(2)
            tel_four   = c3.text_input("Téléphone")
            adresse_four = c4.text_input("Adresse / Wilaya")
            c5, c6     = st.columns(2)
            nif_four   = c5.text_input("NIF / NIS")
            rib_four   = c6.text_input("RIB Bancaire")
            notes_four = st.text_area("Notes / Conditions commerciales")
            sub_four   = st.form_submit_button("💾 Enregistrer", use_container_width=True)

        if sub_four:
            if not nom_four:
                st.error("Le nom est obligatoire.")
            else:
                data["fournisseurs"].append({
                    "nom": nom_four, "type": type_four,
                    "telephone": tel_four, "adresse": adresse_four,
                    "nif": nif_four, "rib": rib_four, "notes": notes_four,
                })
                save()
                st.success(f"✅ Fournisseur « {nom_four} » enregistré !")

    with tab2:
        fournisseurs = data["fournisseurs"]
        if not fournisseurs:
            st.info("Aucun fournisseur enregistré.")
        else:
            df_f = pd.DataFrame(fournisseurs)[["nom","type","telephone","adresse","nif"]]
            df_f.columns = ["Nom","Catégorie","Téléphone","Adresse","NIF"]
            st.dataframe(df_f, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# 11.  MATÉRIAUX & STOCK
# ══════════════════════════════════════════════════════════════════════════════
elif page == "materiaux":
    st.markdown('<p class="main-title">🧱 Matériaux & Gestion du Stock</p>', unsafe_allow_html=True)
    data = st.session_state.data

    tab1, tab2 = st.tabs(["➕ Mouvement de stock", "📋 État du stock"])

    with tab1:
        with st.form("form_mat"):
            c1, c2 = st.columns(2)
            nom_mat    = c1.text_input("Désignation du matériau *")
            type_mouv  = c2.selectbox("Mouvement", ["Entrée (achat)","Sortie (utilisation)","Retour"])
            c3, c4     = st.columns(2)
            quantite   = c3.number_input("Quantité *", min_value=0.0, step=1.0)
            unite      = c4.selectbox("Unité", ["m³","m²","ml","kg","T","L","Sac","Unité","Palette"])
            c5, c6     = st.columns(2)
            prix_unit  = c5.number_input("Prix unitaire (DA)", min_value=0.0, step=10.0)
            date_mat   = c6.date_input("Date")
            projet_mat = st.selectbox("Projet",
                ["—"] + [p["nom"] for p in data["projets"]])
            fournisseur_mat = st.selectbox("Fournisseur",
                ["—"] + [f["nom"] for f in data["fournisseurs"]])
            notes_mat  = st.text_area("Notes")
            sub_mat    = st.form_submit_button("💾 Enregistrer le mouvement", use_container_width=True)

        if sub_mat:
            if not nom_mat or quantite <= 0:
                st.error("Désignation et quantité obligatoires.")
            else:
                data["materiaux"].append({
                    "designation": nom_mat, "mouvement": type_mouv,
                    "quantite": quantite, "unite": unite,
                    "prix_unit": prix_unit,
                    "montant_total": quantite * prix_unit,
                    "date": str(date_mat),
                    "projet": projet_mat, "fournisseur": fournisseur_mat,
                    "notes": notes_mat,
                })
                save()
                st.success(f"✅ Mouvement enregistré pour « {nom_mat} » !")

    with tab2:
        materiaux = data["materiaux"]
        if not materiaux:
            st.info("Aucun mouvement de stock enregistré.")
        else:
            df_m = pd.DataFrame(materiaux)
            df_m["quantite_nette"] = df_m.apply(
                lambda r: r["quantite"] if "Entrée" in str(r["mouvement"]) else -r["quantite"], axis=1)
            stock = df_m.groupby("designation").agg(
                Stock_net=("quantite_nette","sum"),
                Unité=("unite","first"),
                Valeur_totale=("montant_total","sum"),
            ).reset_index()
            stock.columns = ["Désignation","Stock net","Unité","Valeur totale (DA)"]
            st.dataframe(stock, use_container_width=True, hide_index=True)
            st.markdown(f"**Valeur totale du stock : {stock['Valeur totale (DA)'].sum():,.0f} DA**")

# ══════════════════════════════════════════════════════════════════════════════
# 12.  EXPORT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "export":
    st.markdown('<p class="main-title">📤 Export des Données</p>', unsafe_allow_html=True)
    data = st.session_state.data

    sections = {
        "projets": "Projets",
        "employes": "Employés",
        "assurances": "Assurances",
        "depenses": "Dépenses",
        "cahiers_charge": "Cahiers des charges",
        "impots": "Impôts",
        "transactions_financieres": "Transactions financières",
        "creances": "Créances",
        "fournisseurs": "Fournisseurs",
        "materiaux": "Matériaux",
    }

    for key, label in sections.items():
        records = data.get(key, [])
        if records:
            df_exp = pd.DataFrame(records)
            csv = df_exp.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label=f"📥 Exporter {label} ({len(records)} entrées)",
                data=csv,
                file_name=f"{key}_{date.today()}.csv",
                mime="text/csv",
                use_container_width=True,
            )
        else:
            st.button(f"📥 Exporter {label} (0 entrées)", disabled=True, use_container_width=True)

    st.markdown("---")
    st.subheader("🗑️ Réinitialiser toutes les données")
    if st.checkbox("Je confirme vouloir effacer toutes les données"):
        if st.button("⚠️ Réinitialiser", type="primary"):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            st.session_state.data = load_data()
            st.success("Données réinitialisées.")
            st.rerun()
