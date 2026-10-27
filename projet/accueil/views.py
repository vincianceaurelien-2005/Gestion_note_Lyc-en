from functools import wraps
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.hashers import make_password, check_password

from .models import (
    Eleve, Classe, AnneeScolaire, Matiere, Note,
    Utilisateur, Etablissement,
)


# =====================================================
# DÉCORATEUR LOGIN
# =====================================================

def login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper


def get_etablissement():
    etab = Etablissement.objects.first()
    if etab is None:
        etab = Etablissement.objects.create(
            nom='Gestion Lycée',
            adresse='',
            telephone='',
            email='',
            devise='Travail – Discipline – Succès'
        )
    return etab


# =====================================================
# AUTHENTIFICATION
# =====================================================

def login_view(request):
    if request.session.get('user_id'):
        return redirect('index')

    erreur = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = Utilisateur.objects.filter(nom_utilisateur=username).first()

        if user is None:
            erreur = "Nom d'utilisateur ou mot de passe incorrect."
        else:
            # Support plain text (ancien) et hash Django
            ok = False
            if user.mot_de_passe.startswith('pbkdf2_') or user.mot_de_passe.startswith('argon2'):
                ok = check_password(password, user.mot_de_passe)
            else:
                ok = (user.mot_de_passe == password)
                # Migrer vers hash si login réussi
                if ok:
                    user.mot_de_passe = make_password(password)
                    user.save(update_fields=['mot_de_passe'])

            if ok:
                request.session['user_id'] = user.id
                request.session['username'] = user.nom_utilisateur
                request.session['nom_complet'] = user.nom_complet or user.nom_utilisateur
                return redirect('index')
            else:
                erreur = "Nom d'utilisateur ou mot de passe incorrect."

    return render(request, 'accueil/login.html', {'erreur': erreur})


def logout_view(request):
    request.session.flush()
    return redirect('login')


# =====================================================
# TABLEAU DE BORD
# =====================================================

@login_required
def index(request):
    total_eleves = Eleve.objects.count()
    total_matieres = Matiere.objects.count()
    total_notes = Note.objects.count()
    total_classes = Classe.objects.count()

    moyenne_generale = 0
    if total_notes > 0:
        notes = Note.objects.all()
        total = sum(float(n.note) for n in notes)
        moyenne_generale = round(total / total_notes, 2)

    derniers_eleves = Eleve.objects.select_related('classe').order_by('-created_at')[:5]
    etab = get_etablissement()

    context = {
        'total_eleves': total_eleves,
        'total_matieres': total_matieres,
        'total_notes': total_notes,
        'total_classes': total_classes,
        'moyenne_generale': moyenne_generale,
        'derniers_eleves': derniers_eleves,
        'etab': etab,
    }
    return render(request, 'accueil/index.html', context)


# =====================================================
# ÉLÈVES
# =====================================================

@login_required
def liste_eleves(request):
    eleves = Eleve.objects.select_related('classe', 'annee_scolaire').all()
    classes = Classe.objects.all()
    recherche = request.GET.get('recherche', '').strip()
    classe_id = request.GET.get('classe', '').strip()

    if recherche:
        eleves = eleves.filter(
            Q(matricule__icontains=recherche) |
            Q(nom__icontains=recherche) |
            Q(prenom__icontains=recherche)
        )
    if classe_id:
        eleves = eleves.filter(classe_id=classe_id)

    context = {
        'eleves': eleves,
        'classes': classes,
        'recherche': recherche,
        'classe_selectionnee': classe_id,
        'total_eleves': eleves.count(),
    }
    return render(request, 'accueil/eleves/liste.html', context)


@login_required
def ajouter_eleves(request):
    classes = Classe.objects.all()

    if request.method == 'POST':
        matricule = request.POST.get('matricule', '').strip()
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        sexe = request.POST.get('sexe', '').strip()
        date_naissance = request.POST.get('date_naissance') or None
        classe_id = request.POST.get('classe')

        if not matricule or not nom or not prenom or not sexe or not classe_id:
            return render(request, 'accueil/eleves/ajouter.html', {
                'classes': classes,
                'erreur': 'Veuillez remplir tous les champs obligatoires.'
            })

        if Eleve.objects.filter(matricule=matricule).exists():
            return render(request, 'accueil/eleves/ajouter.html', {
                'classes': classes,
                'erreur': 'Ce matricule existe déjà.'
            })

        classe = get_object_or_404(Classe, id=classe_id)
        annee = AnneeScolaire.objects.filter(active=True).first()
        if annee is None:
            return render(request, 'accueil/eleves/ajouter.html', {
                'classes': classes,
                'erreur': 'Aucune année scolaire active. Activez-en une dans Paramètres.'
            })

        Eleve.objects.create(
            matricule=matricule, nom=nom, prenom=prenom, sexe=sexe,
            date_naissance=date_naissance, classe=classe, annee_scolaire=annee
        )
        return redirect('liste_eleves')

    return render(request, 'accueil/eleves/ajouter.html', {'classes': classes})


@login_required
def detail_eleve(request, id):
    eleve = get_object_or_404(Eleve.objects.select_related('classe', 'annee_scolaire'), id=id)
    notes = Note.objects.filter(eleve=eleve).select_related('matiere')
    return render(request, 'accueil/eleves/detail.html', {
        'eleve': eleve,
        'notes': notes,
    })


@login_required
def modifier_eleve(request, id):
    eleve = get_object_or_404(Eleve, id=id)
    classes = Classe.objects.all()

    if request.method == 'POST':
        matricule = request.POST.get('matricule', '').strip()
        nom = request.POST.get('nom', '').strip()
        prenom = request.POST.get('prenom', '').strip()
        sexe = request.POST.get('sexe', '').strip()
        date_naissance = request.POST.get('date_naissance') or None
        classe_id = request.POST.get('classe')

        if not matricule or not nom or not prenom or not sexe or not classe_id:
            return render(request, 'accueil/eleves/modifier.html', {
                'eleve': eleve, 'classes': classes,
                'erreur': 'Veuillez remplir tous les champs obligatoires.'
            })

        if Eleve.objects.filter(matricule=matricule).exclude(id=id).exists():
            return render(request, 'accueil/eleves/modifier.html', {
                'eleve': eleve, 'classes': classes,
                'erreur': 'Ce matricule existe déjà.'
            })

        classe = get_object_or_404(Classe, id=classe_id)
        eleve.matricule = matricule
        eleve.nom = nom
        eleve.prenom = prenom
        eleve.sexe = sexe
        eleve.date_naissance = date_naissance
        eleve.classe = classe
        eleve.save()
        return redirect('detail_eleve', id=eleve.id)

    return render(request, 'accueil/eleves/modifier.html', {
        'eleve': eleve, 'classes': classes
    })


@login_required
def supprimer_eleve(request, id):
    eleve = get_object_or_404(Eleve, id=id)
    if request.method == 'POST':
        eleve.delete()
    return redirect('liste_eleves')


# =====================================================
# MATIÈRES
# =====================================================

@login_required
def Liste_matieres(request):
    matieres = Matiere.objects.select_related('classe').all()
    recherche = request.GET.get('recherche', '').strip()
    classe_id = request.GET.get('classe', '').strip()
    classes = Classe.objects.all()

    if recherche:
        matieres = matieres.filter(
            Q(code__icontains=recherche) | Q(nom__icontains=recherche)
        )
    if classe_id:
        matieres = matieres.filter(classe_id=classe_id)

    context = {
        'matieres': matieres,
        'classes': classes,
        'recherche': recherche,
        'classe_selectionnee': classe_id,
        'total_matieres': matieres.count(),
    }
    return render(request, 'accueil/matieres/ListesMatieres.html', context)


@login_required
def ajouter_matieres(request):
    classes = Classe.objects.all()
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        nom = request.POST.get('nom', '').strip()
        coefficient = request.POST.get('coefficient', '').strip()
        classe_id = request.POST.get('classe')

        if not code or not nom or not coefficient or not classe_id:
            return render(request, 'accueil/matieres/ajouterMatieres.html', {
                'classes': classes, 'erreur': 'Veuillez remplir tous les champs.'
            })
        if Matiere.objects.filter(code=code).exists():
            return render(request, 'accueil/matieres/ajouterMatieres.html', {
                'classes': classes, 'erreur': 'Ce code matière existe déjà.'
            })

        classe = get_object_or_404(Classe, id=classe_id)
        Matiere.objects.create(code=code, nom=nom, coefficient=coefficient, classe=classe)
        return redirect('liste_matieres')

    return render(request, 'accueil/matieres/ajouterMatieres.html', {'classes': classes})


@login_required
def detail_matiere(request, id):
    matiere = get_object_or_404(Matiere.objects.select_related('classe'), id=id)
    return render(request, 'accueil/matieres/detail.html', {'matiere': matiere})


@login_required
def modifier_matiere(request, id):
    matiere = get_object_or_404(Matiere, id=id)
    classes = Classe.objects.all()

    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        nom = request.POST.get('nom', '').strip()
        coefficient = request.POST.get('coefficient', '').strip()
        classe_id = request.POST.get('classe')

        if not code or not nom or not coefficient or not classe_id:
            return render(request, 'accueil/matieres/modifier.html', {
                'matiere': matiere, 'classes': classes,
                'erreur': 'Veuillez remplir tous les champs.'
            })
        if Matiere.objects.filter(code=code).exclude(id=id).exists():
            return render(request, 'accueil/matieres/modifier.html', {
                'matiere': matiere, 'classes': classes,
                'erreur': 'Ce code matière existe déjà.'
            })

        classe = get_object_or_404(Classe, id=classe_id)
        matiere.code = code
        matiere.nom = nom
        matiere.coefficient = coefficient
        matiere.classe = classe
        matiere.save()
        return redirect('detail_matiere', id=matiere.id)

    return render(request, 'accueil/matieres/modifier.html', {
        'matiere': matiere, 'classes': classes
    })


@login_required
def supprimer_matiere(request, id):
    matiere = get_object_or_404(Matiere, id=id)
    if request.method == 'POST':
        matiere.delete()
    return redirect('liste_matieres')


# =====================================================
# NOTES
# =====================================================

@login_required
def liste_notes(request):
    notes = Note.objects.select_related(
        'eleve', 'matiere', 'annee_scolaire'
    ).all()
    return render(request, 'accueil/notes.html', {'notes': notes})


@login_required
def ajouter_note(request):
    eleves = Eleve.objects.select_related('classe').all()
    matieres = Matiere.objects.select_related('classe').all()

    if request.method == 'POST':
        try:
            eleve = get_object_or_404(Eleve, id=request.POST.get('eleve'))
            matiere = get_object_or_404(Matiere, id=request.POST.get('matiere'))
            trimestre = int(request.POST.get('trimestre'))
            note_val = request.POST.get('note')
            annee = AnneeScolaire.objects.filter(active=True).first() or eleve.annee_scolaire

            Note.objects.update_or_create(
                eleve=eleve, matiere=matiere,
                annee_scolaire=annee, trimestre=trimestre,
                defaults={'note': note_val}
            )
            return redirect('liste_notes')
        except Exception as e:
            return render(request, 'accueil/note_form.html', {
                'eleves': eleves, 'matieres': matieres, 'erreur': str(e)
            })

    return render(request, 'accueil/note_form.html', {
        'eleves': eleves, 'matieres': matieres
    })


# =====================================================
# RÉSULTATS
# =====================================================

@login_required
def resultats(request):
    rows = []
    for eleve in Eleve.objects.select_related('classe').all():
        notes = Note.objects.filter(eleve=eleve).select_related('matiere')
        if notes.exists():
            total_pondere = sum(float(n.note) * float(n.matiere.coefficient) for n in notes)
            total_coeff = sum(float(n.matiere.coefficient) for n in notes)
            moyenne = round(total_pondere / total_coeff, 2) if total_coeff else None
        else:
            moyenne = None
        rows.append({'eleve': eleve, 'moyenne': moyenne})
    return render(request, 'accueil/resultats.html', {'rows': rows})


# =====================================================
# BULLETIN PDF (reportlab – marche bien sur Windows)
# =====================================================

@login_required
def bulletin_pdf(request, id):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
    )
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from io import BytesIO

    eleve = get_object_or_404(
        Eleve.objects.select_related('classe', 'annee_scolaire'), id=id
    )
    notes = Note.objects.filter(eleve=eleve).select_related('matiere').order_by('matiere__nom')
    etab = get_etablissement()

    if notes.exists():
        total_pondere = sum(float(n.note) * float(n.matiere.coefficient) for n in notes)
        total_coeff = sum(float(n.matiere.coefficient) for n in notes)
        moyenne = round(total_pondere / total_coeff, 2) if total_coeff else None
    else:
        moyenne = None

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=1.5*cm, leftMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleFR', parent=styles['Heading1'],
        alignment=TA_CENTER, fontSize=16, spaceAfter=6, textColor=colors.HexColor('#1e3a5f')
    )
    subtitle = ParagraphStyle(
        'Sub', parent=styles['Normal'],
        alignment=TA_CENTER, fontSize=11, spaceAfter=4
    )
    normal = ParagraphStyle('N', parent=styles['Normal'], fontSize=10, spaceAfter=3)
    right = ParagraphStyle('R', parent=styles['Normal'], alignment=TA_RIGHT, fontSize=10)

    story = []
    story.append(Paragraph(etab.nom.upper(), title_style))
    if etab.adresse:
        story.append(Paragraph(etab.adresse, subtitle))
    if etab.telephone or etab.email:
        contact = ' | '.join(filter(None, [etab.telephone, etab.email]))
        story.append(Paragraph(contact, subtitle))
    if etab.devise:
        story.append(Paragraph(f'<i>{etab.devise}</i>', subtitle))

    story.append(Spacer(1, 8))
    story.append(HRFlowable(width='100%', thickness=1.5, color=colors.HexColor('#1e3a5f')))
    story.append(Spacer(1, 10))
    story.append(Paragraph('<b>BULLETIN DE NOTES</b>', title_style))
    story.append(Spacer(1, 12))

    info_data = [
        [Paragraph(f'<b>Élève :</b> {eleve.nom} {eleve.prenom}', normal),
         Paragraph(f'<b>Matricule :</b> {eleve.matricule}', right)],
        [Paragraph(f'<b>Classe :</b> {eleve.classe.nom}', normal),
         Paragraph(f'<b>Année :</b> {eleve.annee_scolaire.libelle}', right)],
        [Paragraph(f'<b>Sexe :</b> {"Masculin" if eleve.sexe == "M" else "Féminin"}', normal),
         Paragraph('', right)],
    ]
    info_table = Table(info_data, colWidths=[9*cm, 8*cm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 16))

    # Tableau notes
    header = ['Matière', 'Code', 'Coef.', 'Trim.', 'Note /20']
    data = [header]
    for n in notes:
        data.append([
            n.matiere.nom,
            n.matiere.code,
            str(n.matiere.coefficient),
            f'T{n.trimestre}',
            f'{n.note}',
        ])

    if not notes:
        data.append(['Aucune note enregistrée', '', '', '', ''])

    col_widths = [7*cm, 3*cm, 2*cm, 2*cm, 3*cm]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (2, 0), (-1, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#94a3b8')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 18))

    moy_text = f'{moyenne}/20' if moyenne is not None else '—'
    story.append(Paragraph(f'<b>Moyenne générale (pondérée) : {moy_text}</b>', normal))
    story.append(Spacer(1, 30))

    story.append(Paragraph(
        f'Fait le ________________  &nbsp;&nbsp;&nbsp; Signature du Directeur',
        normal
    ))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    filename = f'bulletin_{eleve.matricule}.pdf'
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    return response


# =====================================================
# PARAMÈTRES
# =====================================================

@login_required
def parametres(request):
    etab = get_etablissement()
    user = Utilisateur.objects.filter(id=request.session.get('user_id')).first()
    annees = AnneeScolaire.objects.all().order_by('-libelle')
    message_ok = None
    erreur = None

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'etablissement':
            etab.nom = request.POST.get('nom_etab', '').strip() or etab.nom
            etab.adresse = request.POST.get('adresse', '').strip()
            etab.telephone = request.POST.get('telephone', '').strip()
            etab.email = request.POST.get('email', '').strip()
            etab.devise = request.POST.get('devise', '').strip()
            etab.save()
            message_ok = 'Informations de l\'établissement enregistrées.'

        elif action == 'profil' and user:
            user.nom_complet = request.POST.get('nom_complet', '').strip()
            user.contact = request.POST.get('contact', '').strip()
            new_pass = request.POST.get('nouveau_password', '').strip()
            if new_pass:
                user.mot_de_passe = make_password(new_pass)
            user.save()
            request.session['nom_complet'] = user.nom_complet or user.nom_utilisateur
            message_ok = 'Profil mis à jour.'

        elif action == 'annee':
            annee_id = request.POST.get('annee_active')
            if annee_id:
                AnneeScolaire.objects.update(active=False)
                AnneeScolaire.objects.filter(id=annee_id).update(active=True)
                message_ok = 'Année scolaire active mise à jour.'

        elif action == 'ajouter_annee':
            libelle = request.POST.get('nouvelle_annee', '').strip()
            if libelle:
                if AnneeScolaire.objects.filter(libelle=libelle).exists():
                    erreur = 'Cette année existe déjà.'
                else:
                    AnneeScolaire.objects.create(libelle=libelle, active=False)
                    message_ok = f'Année {libelle} ajoutée.'

    # Recharger
    etab = get_etablissement()
    user = Utilisateur.objects.filter(id=request.session.get('user_id')).first()
    annees = AnneeScolaire.objects.all().order_by('-libelle')

    return render(request, 'accueil/parametres.html', {
        'etab': etab,
        'user': user,
        'annees': annees,
        'message_ok': message_ok,
        'erreur': erreur,
    })
