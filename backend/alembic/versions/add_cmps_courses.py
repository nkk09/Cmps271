"""Add remaining CMPS courses, professors, and sections for Spring 2026.

Revision ID: add_cmps_courses
Revises: relax_legacy_violations_reason
Create Date: 2026-04-28
"""

from alembic import op
import sqlalchemy as sa
from typing import Sequence, Union

revision: str = 'add_cmps_courses'
down_revision: Union[str, Sequence[str], None] = 'relax_legacy_violations_reason'
branch_labels = None
depends_on = None


def upgrade() -> None:
    SEM = 'f58720e7-9879-4876-90c4-be4bc4b342cc'

    # ── Existing professor IDs (from seed_courses) ─────────────────────────
    ZALGHOUT    = '473d05bd-aa18-4370-9ff1-ecb8d32af73f'
    GHANNAM     = 'e7d2952b-0b0a-40d9-86ec-92b38ee4587e'
    KHALIL      = 'ae9e1e32-1225-495c-93e9-157643279c6b'
    AOUDE       = '7f83c43c-5a4c-42fc-8ffd-e246ce130129'
    EL_HAJJ_M   = 'db937c05-b8b3-4692-b858-64da790373ce'  # Mohamed El Hajj
    ELFIL       = '4cd7134d-8f6b-4ebd-ac38-7618ee56b64b'
    NEHME       = '4108b15f-0d08-430c-9866-e49f4b4cbdc4'
    FATAIRI     = 'cdf16f41-9043-431b-9601-b658a39267df'

    # ── Existing course IDs (from seed_courses) ────────────────────────────
    CMPS203 = 'CMPS 203'

    # ── New professor IDs ──────────────────────────────────────────────────
    CHEHABEDDINE = '00000000-0000-4000-8000-000000000001'
    HAMAMJI      = '00000000-0000-4000-8000-000000000002'
    SEIFEDDINE   = '00000000-0000-4000-8000-000000000003'
    EL_MASRI     = '00000000-0000-4000-8000-000000000004'
    CHEHAB       = '00000000-0000-4000-8000-000000000005'
    RAHEEL       = '00000000-0000-4000-8000-000000000006'
    SAADIE       = '00000000-0000-4000-8000-000000000007'
    JARJOUR      = '00000000-0000-4000-8000-000000000008'
    FAWAZ        = '00000000-0000-4000-8000-000000000009'
    SOBH         = '00000000-0000-4000-8000-000000000010'
    HARAJLI      = '00000000-0000-4000-8000-000000000011'
    DARWICH      = '00000000-0000-4000-8000-000000000012'
    FATAYRI      = '00000000-0000-4000-8000-000000000013'
    ABU_SALEM    = '00000000-0000-4000-8000-000000000014'
    KOBEISSI     = '00000000-0000-4000-8000-000000000015'
    HAZIM        = '00000000-0000-4000-8000-000000000016'
    FIDAWI       = '00000000-0000-4000-8000-000000000017'
    ABDALLAH     = '00000000-0000-4000-8000-000000000018'
    RAMLAOUI     = '00000000-0000-4000-8000-000000000019'
    EL_HAJJ_I    = '00000000-0000-4000-8000-000000000020'  # Izzat El Hajj
    AOUN         = '00000000-0000-4000-8000-000000000021'
    JUREIDINI    = '00000000-0000-4000-8000-000000000022'
    ELMOGHRABY   = '00000000-0000-4000-8000-000000000023'
    AINTABLIAN   = '00000000-0000-4000-8000-000000000024'
    HARKOUS      = '00000000-0000-4000-8000-000000000025'
    EL_HAJJ_W    = '00000000-0000-4000-8000-000000000026'  # Wassim El Hajj
    ELBASSUONI   = '00000000-0000-4000-8000-000000000027'
    FARRAN_R     = '00000000-0000-4000-8000-000000000028'  # Rami Farran
    YASSEEN      = '00000000-0000-4000-8000-000000000029'
    ASSAF        = '00000000-0000-4000-8000-000000000030'
    SAKR         = '00000000-0000-4000-8000-000000000031'
    EL_KHOURY    = '00000000-0000-4000-8000-000000000032'
    NOUREDDINE   = '00000000-0000-4000-8000-000000000033'
    ABDO_MOUAWAD = '00000000-0000-4000-8000-000000000034'
    KHABBAZ      = '00000000-0000-4000-8000-000000000035'
    SAFA         = '00000000-0000-4000-8000-000000000036'
    KAYAL        = '00000000-0000-4000-8000-000000000037'
    WEHBI        = '00000000-0000-4000-8000-000000000038'
    SHARAFEDDINE = '00000000-0000-4000-8000-000000000039'

    # ── New course IDs ─────────────────────────────────────────────────────
    CMPS202   = 'CMPS 202'
    CMPS208   = 'CMPS 208'
    CMPS211   = 'CMPS 211'
    CMPS214   = 'CMPS 214'
    CMPS215   = 'CMPS 215'
    CMPS221   = 'CMPS 221'
    CMPS224   = 'CMPS 224'
    CMPS231   = 'CMPS 231'
    CMPS232   = 'CMPS 232'
    CMPS240   = 'CMPS 240'
    CMPS241   = 'CMPS 241'
    CMPS242   = 'CMPS 242'
    CMPS243   = 'CMPS 243'
    CMPS244   = 'CMPS 244'
    CMPS261   = 'CMPS 261'
    CMPS262   = 'CMPS 262'
    CMPS271   = 'CMPS 271'
    CMPS279   = 'CMPS 279'
    CMPS288   = 'CMPS 288'
    CMPS297AF = 'CMPS 297AF'
    CMPS297U  = 'CMPS 297U'
    CMPS297Z  = 'CMPS 297Z'
    CMPS299   = 'CMPS 299'
    CMPS299A  = 'CMPS 299A'
    CMPS299B  = 'CMPS 299B'
    CMPS302   = 'CMPS 302'
    CMPS324   = 'CMPS 324'
    CMPS332   = 'CMPS 332'
    CMPS351   = 'CMPS 351'
    CMPS395A  = 'CMPS 395A'
    CMPS396AK = 'CMPS 396AK'
    CMPS398   = 'CMPS 398'
    CMPS399   = 'CMPS 399'
    CMPS399A  = 'CMPS 399A'
    CMPS399B  = 'CMPS 399B'
    CMPS399C  = 'CMPS 399C'

    x = op.execute

    # ── New courses (ON CONFLICT DO NOTHING handles pre-existing rows) ─────
    def c(code, title, attrs=None):
        if attrs:
            x(sa.text(
                f"INSERT INTO courses (id, code, title, department, attributes) "
                f"VALUES (gen_random_uuid(), '{code}', '{title}', 'CMPS', ARRAY[{attrs}]) "
                f"ON CONFLICT (code) DO NOTHING"
            ))
        else:
            x(sa.text(
                f"INSERT INTO courses (id, code, title, department) "
                f"VALUES (gen_random_uuid(), '{code}', '{title}', 'CMPS') "
                f"ON CONFLICT (code) DO NOTHING"
            ))

    c('CMPS 202',   'Data Structures')
    c('CMPS 208',   'Computing for Business')
    c('CMPS 211',   'Discrete Structures')
    c('CMPS 214',   'Design & Analysis of Algorithms')
    c('CMPS 215',   'Theory of Computation')
    c('CMPS 221',   'Computer Organization & Design')
    c('CMPS 224',   'GPU Computing')
    c('CMPS 231',   'Programming Languages')
    c('CMPS 232',   'Compiler Construction')
    c('CMPS 240',   'Operating Systems')
    c('CMPS 241',   'Systems Programming')
    c('CMPS 242',   'Computer Networks')
    c('CMPS 243',   'Computer & Information Security')
    c('CMPS 244',   'Database Systems')
    c('CMPS 261',   'Machine Learning')
    c('CMPS 262',   'Data Science')
    c('CMPS 271',   'Software Engineering')
    c('CMPS 279',   'Mobile Application Development')
    c('CMPS 288',   'Game Programming')
    c('CMPS 297AF', 'ST.Intro. to Bioinformatics')
    c('CMPS 297U',  'ST. Cloud Computing')
    c('CMPS 297Z',  'ST.Optimization Non-Linear Pro')
    c('CMPS 299',   'Capstone Project',  "'Writing in the Discipline'")
    c('CMPS 299A',  'Capstone Project',  "'Writing in the Discipline'")
    c('CMPS 299B',  'Capstone Project',  "'Writing in the Discipline'")
    c('CMPS 302',   'Computing Systems')
    c('CMPS 324',   'GPU Computing')
    c('CMPS 332',   'Compiler Construction')
    c('CMPS 351',   'Optimization & Nonlinear Problem')
    c('CMPS 395A',  'Comprehensive Exam')
    c('CMPS 396AK', 'ST.Reinforcement Learning')
    c('CMPS 398',   'MS Project')
    c('CMPS 399',   'Thesis')
    c('CMPS 399A',  'Thesis')
    c('CMPS 399B',  'Thesis')
    c('CMPS 399C',  'Thesis')

    # ── New professors (ON CONFLICT (id) DO NOTHING for idempotency) ─────
    def p(pid, first, last):
        x(sa.text(
            f"INSERT INTO professors (id, first_name, last_name) "
            f"VALUES ('{pid}', '{first}', '{last}') "
            f"ON CONFLICT (id) DO NOTHING"
        ))

    p(CHEHABEDDINE, 'Zein',          'Chehabeddine')
    p(HAMAMJI,      'Sam',           'Hamamji')
    p(SEIFEDDINE,   'Jad',           'Seifeddine')
    p(EL_MASRI,     'Maya',          'El Masri')
    p(CHEHAB,       'Mohamad',       'Chehab')
    p(RAHEEL,       'Saeed',         'Raheel')
    p(SAADIE,       'Razan',         'Saadie')
    p(JARJOUR,      'Moustafa',      'Jarjour')
    p(FAWAZ,        'Hassan',        'Fawaz')
    p(SOBH,         'Amine',         'Sobh')
    p(HARAJLI,      'Nour Alzahraa', 'Harajli')
    p(DARWICH,      'Rawan',         'Darwich')
    p(FATAYRI,      'Mostafa',       'Fatayri')
    p(ABU_SALEM,    'Fatima',        'Abu Salem')
    p(KOBEISSI,     'Mohamed A.',    'Kobeissi')
    p(HAZIM,        'Mohamad',       'Hazim')
    p(FIDAWI,       'Raed',          'Fidawi')
    p(ABDALLAH,     'Maher',         'Abdallah')
    p(RAMLAOUI,     'Hussam',        'Ramlaoui')
    p(EL_HAJJ_I,    'Izzat',         'El Hajj')
    p(AOUN,         'Zeina',         'Aoun')
    p(JUREIDINI,    'Wadi''',        'Jureidini')
    p(ELMOGHRABY,   'Jad',           'Elmoghraby')
    p(AINTABLIAN,   'Nanar',         'Aintablian')
    p(HARKOUS,      'Hasanin',       'Harkous')
    p(EL_HAJJ_W,    'Wassim',        'El Hajj')
    p(ELBASSUONI,   'Shady',         'Elbassuoni')
    p(FARRAN_R,     'Rami',          'Farran')
    p(YASSEEN,      'Zahraa',        'Yasseen')
    p(ASSAF,        'Rida',          'Assaf')
    p(SAKR,         'Mohamad',       'Sakr')
    p(EL_KHOURY,    'Georges',       'El Khoury')
    p(NOUREDDINE,   'Moustafa',      'Noureddine')
    p(ABDO_MOUAWAD, 'Amer',          'Abdo Mouawad')
    p(KHABBAZ,      'Maurice',       'Khabbaz')
    p(SAFA,         'Haidar',        'Safa')
    p(KAYAL,        'Aya',           'Kayal')
    p(WEHBI,        'Sarry',         'Wehbi')
    p(SHARAFEDDINE, 'Sanaa',         'Sharafeddine')

    # ── Sections: look up course_id by code so pre-existing courses work ──
    def s(crn, course_code, prof, credits):
        x(sa.text(
            f"INSERT INTO sections (id, course_id, professor_id, semester_id, section_number, credits) "
            f"SELECT '00000000-0000-4000-8000-0000000{crn}', id, '{prof}', '{SEM}', '{crn}', {credits} "
            f"FROM courses WHERE code = '{course_code}' "
            f"ON CONFLICT (id) DO NOTHING"
        ))

    # CMPS 202 – Data Structures
    s('20805', CMPS202, CHEHABEDDINE, 0)
    s('20807', CMPS202, HAMAMJI,      0)
    s('20811', CMPS202, SEIFEDDINE,   0)
    s('20812', CMPS202, EL_MASRI,     0)
    s('20813', CMPS202, EL_MASRI,     0)
    s('20815', CMPS202, CHEHAB,       0)
    s('20817', CMPS202, RAHEEL,       3)
    s('20818', CMPS202, AOUDE,        3)
    s('20819', CMPS202, AOUDE,        3)

    # CMPS 203 – missing section B2
    s('20821', CMPS203, SAADIE, 0)

    # CMPS 208 – Computing for Business
    s('20833', CMPS208, JARJOUR,   0)
    s('20834', CMPS208, NEHME,     0)
    s('20835', CMPS208, FAWAZ,     0)
    s('20838', CMPS208, FAWAZ,     0)
    s('20839', CMPS208, SOBH,      0)
    s('20840', CMPS208, JARJOUR,   0)
    s('20841', CMPS208, HARAJLI,   0)
    s('20842', CMPS208, SOBH,      0)
    s('20843', CMPS208, HARAJLI,   0)
    s('20845', CMPS208, EL_HAJJ_M, 3)
    s('20846', CMPS208, GHANNAM,   3)
    s('20847', CMPS208, FATAIRI,   3)

    # CMPS 211 – Discrete Structures
    s('20852', CMPS211, GHANNAM, 0)
    s('20853', CMPS211, DARWICH, 0)
    s('20854', CMPS211, FATAYRI, 0)
    s('20855', CMPS211, KHALIL,  3)
    s('20856', CMPS211, KHALIL,  3)
    s('20857', CMPS211, RAHEEL,  3)

    # CMPS 214 – Design & Analysis of Algorithms
    s('20858', CMPS214, WEHBI,     0)
    s('20859', CMPS214, ELFIL,     0)
    s('20860', CMPS214, ABU_SALEM, 3)
    s('20861', CMPS214, ABU_SALEM, 3)

    # CMPS 215 – Theory of Computation
    s('20864', CMPS215, KOBEISSI, 3)
    s('20865', CMPS215, ABDALLAH, 3)

    # CMPS 221 – Computer Organization & Design
    s('20866', CMPS221, RAMLAOUI, 3)

    # CMPS 224 – GPU Computing (undergrad)
    s('20867', CMPS224, EL_HAJJ_I, 3)

    # CMPS 231 – Programming Languages
    s('20868', CMPS231, RAHEEL, 3)
    s('20869', CMPS231, RAHEEL, 3)

    # CMPS 232 – Compiler Construction (undergrad)
    s('20870', CMPS232, EL_HAJJ_I, 3)

    # CMPS 240 – Operating Systems
    s('20871', CMPS240, KHABBAZ,  3)
    s('20872', CMPS240, RAMLAOUI, 3)

    # CMPS 241 – Systems Programming
    s('20873', CMPS241, ZALGHOUT, 3)

    # CMPS 242 – Computer Networks
    s('20874', CMPS242, KHABBAZ, 3)

    # CMPS 243 – Computer & Information Security
    s('20875', CMPS243, AOUN, 3)

    # CMPS 244 – Database Systems
    s('20876', CMPS244, JUREIDINI, 3)
    s('20878', CMPS244, JUREIDINI, 3)
    s('20879', CMPS244, JUREIDINI, 3)

    # CMPS 261 – Machine Learning
    s('20880', CMPS261, ELMOGHRABY, 0)
    s('20881', CMPS261, AINTABLIAN, 0)
    s('20882', CMPS261, HARKOUS,    3)
    s('20883', CMPS261, KOBEISSI,   3)

    # CMPS 262 – Data Science
    s('20884', CMPS262, ABDALLAH, 3)

    # CMPS 271 – Software Engineering
    s('20886', CMPS271, ZALGHOUT,   3)
    s('20887', CMPS271, SAKR,       3)
    s('20888', CMPS271, EL_KHOURY,  3)
    s('20889', CMPS271, NOUREDDINE, 3)

    # CMPS 279 – Mobile Application Development
    s('20890', CMPS279, FARRAN_R, 3)

    # CMPS 288 – Game Programming
    s('20891', CMPS288, YASSEEN, 3)

    # CMPS 297AF – ST.Intro. to Bioinformatics
    s('20892', CMPS297AF, ASSAF, 3)

    # CMPS 297U – ST. Cloud Computing
    s('20893', CMPS297U, HARKOUS, 3)

    # CMPS 297Z – ST.Optimization Non-Linear Pro
    s('20894', CMPS297Z, KOBEISSI, 3)

    # CMPS 299 – Capstone Project
    s('20895', CMPS299, ABDO_MOUAWAD, 3)
    s('20896', CMPS299, KHABBAZ,      3)
    s('20897', CMPS299, KOBEISSI,     3)
    s('20898', CMPS299, ASSAF,        3)
    s('20899', CMPS299, RAHEEL,       3)
    s('20900', CMPS299, HARKOUS,      3)
    s('20901', CMPS299, SAFA,         3)
    s('20902', CMPS299, EL_HAJJ_I,    3)
    s('20903', CMPS299, ZALGHOUT,     3)
    s('20904', CMPS299, SAKR,         3)
    s('20905', CMPS299, ABU_SALEM,    3)
    s('20906', CMPS299, JUREIDINI,    3)
    s('20907', CMPS299, ELBASSUONI,   3)
    s('23267', CMPS299, EL_HAJJ_W,    3)

    # CMPS 299A – Capstone Project (1 credit)
    s('20908', CMPS299A, SAFA,         1)
    s('20909', CMPS299A, HARKOUS,      1)
    s('20910', CMPS299A, SAKR,         1)
    s('20911', CMPS299A, ZALGHOUT,     1)
    s('20912', CMPS299A, KOBEISSI,     1)
    s('20913', CMPS299A, ELBASSUONI,   1)
    s('20914', CMPS299A, ABU_SALEM,    1)
    s('20915', CMPS299A, KHABBAZ,      1)
    s('20916', CMPS299A, ABDO_MOUAWAD, 1)
    s('20917', CMPS299A, RAHEEL,       1)
    s('20918', CMPS299A, ASSAF,        1)
    s('20919', CMPS299A, JUREIDINI,    1)
    s('20920', CMPS299A, EL_HAJJ_I,    1)

    # CMPS 299B – Capstone Project (2 credits)
    s('20921', CMPS299B, KHABBAZ,      2)
    s('20922', CMPS299B, ASSAF,        2)
    s('20923', CMPS299B, SAKR,         2)
    s('20924', CMPS299B, ZALGHOUT,     2)
    s('20925', CMPS299B, KOBEISSI,     2)
    s('20926', CMPS299B, SAFA,         2)
    s('20927', CMPS299B, JUREIDINI,    2)
    s('20928', CMPS299B, EL_HAJJ_I,    2)
    s('20929', CMPS299B, ABU_SALEM,    2)
    s('20930', CMPS299B, HARKOUS,      2)
    s('20931', CMPS299B, RAHEEL,       2)
    s('20932', CMPS299B, ABDO_MOUAWAD, 2)
    s('20933', CMPS299B, ELBASSUONI,   2)

    # CMPS 302 – Computing Systems (grad)
    s('20934', CMPS302, SAFA, 3)

    # CMPS 324 – GPU Computing (grad)
    s('20935', CMPS324, EL_HAJJ_I, 3)

    # CMPS 332 – Compiler Construction (grad)
    s('20936', CMPS332, EL_HAJJ_I, 3)

    # CMPS 351 – Optimization & Nonlinear Problem (grad)
    s('20937', CMPS351, KOBEISSI, 3)

    # CMPS 395A – Comprehensive Exam
    s('20939', CMPS395A, ABU_SALEM, 0)

    # CMPS 396AK – ST.Reinforcement Learning
    s('20940', CMPS396AK, KAYAL, 3)

    # CMPS 398 – MS Project
    s('20942', CMPS398, ELBASSUONI, 3)

    # CMPS 399 – Thesis (9 credits)
    s('20943', CMPS399, ABU_SALEM,    9)
    s('20944', CMPS399, EL_HAJJ_I,    9)
    s('20945', CMPS399, SAFA,         9)
    s('20946', CMPS399, ELBASSUONI,   9)
    s('23276', CMPS399, SAKR,         9)
    s('23277', CMPS399, ABDO_MOUAWAD, 9)
    s('23279', CMPS399, HARKOUS,      9)
    s('23280', CMPS399, ASSAF,        9)
    s('23281', CMPS399, KHABBAZ,      9)
    s('23408', CMPS399, KAYAL,        9)

    # CMPS 399A – Thesis (9 credits)
    s('20947', CMPS399A, ABU_SALEM,    9)
    s('20948', CMPS399A, ELBASSUONI,   9)
    s('23284', CMPS399A, EL_HAJJ_I,    9)
    s('23285', CMPS399A, SAFA,         9)
    s('23286', CMPS399A, SAKR,         9)
    s('23409', CMPS399A, ABDO_MOUAWAD, 9)
    s('23410', CMPS399A, HARKOUS,      9)
    s('23411', CMPS399A, ASSAF,        9)
    s('23412', CMPS399A, KHABBAZ,      9)
    s('23413', CMPS399A, KAYAL,        9)

    # CMPS 399B – Thesis (9 credits)
    s('23414', CMPS399B, ABU_SALEM,    9)
    s('20949', CMPS399B, SAFA,         9)
    s('23415', CMPS399B, ABDO_MOUAWAD, 9)
    s('23416', CMPS399B, HARKOUS,      9)
    s('23417', CMPS399B, EL_HAJJ_I,    9)
    s('23418', CMPS399B, SAKR,         9)
    s('23419', CMPS399B, ASSAF,        9)
    s('23420', CMPS399B, KHABBAZ,      9)
    s('23421', CMPS399B, ELBASSUONI,   9)
    s('23422', CMPS399B, KAYAL,        9)

    # CMPS 399C – Thesis (9 credits)
    s('20950', CMPS399C, ABU_SALEM,    9)
    s('20951', CMPS399C, SAFA,         9)
    s('23322', CMPS399C, ASSAF,        9)
    s('23423', CMPS399C, ABDO_MOUAWAD, 9)
    s('23424', CMPS399C, HARKOUS,      9)
    s('23425', CMPS399C, EL_HAJJ_I,    9)
    s('23426', CMPS399C, SAKR,         9)
    s('23427', CMPS399C, KHABBAZ,      9)
    s('23428', CMPS399C, KAYAL,        9)
    s('23429', CMPS399C, ELBASSUONI,   9)
    s('23485', CMPS399C, SHARAFEDDINE, 9)


def downgrade() -> None:
    new_crns = [
        '20805','20807','20811','20812','20813','20815','20817','20818','20819',
        '20821',
        '20833','20834','20835','20838','20839','20840','20841','20842','20843',
        '20845','20846','20847',
        '20852','20853','20854','20855','20856','20857',
        '20858','20859','20860','20861',
        '20864','20865',
        '20866','20867','20868','20869','20870','20871','20872','20873','20874',
        '20875','20876','20878','20879',
        '20880','20881','20882','20883','20884',
        '20886','20887','20888','20889','20890','20891','20892','20893','20894',
        '20895','20896','20897','20898','20899','20900','20901','20902','20903',
        '20904','20905','20906','20907',
        '20908','20909','20910','20911','20912','20913','20914','20915','20916',
        '20917','20918','20919','20920',
        '20921','20922','20923','20924','20925','20926','20927','20928','20929',
        '20930','20931','20932','20933',
        '20934','20935','20936','20937','20939','20940','20942',
        '20943','20944','20945','20946','20947','20948','20949','20950','20951',
        '23267','23276','23277','23279','23280','23281',
        '23284','23285','23286',
        '23322',
        '23408','23409','23410','23411','23412','23413',
        '23414','23415','23416','23417','23418','23419','23420','23421','23422',
        '23423','23424','23425','23426','23427','23428','23429','23485',
    ]
    crn_list = ', '.join(f"'{c}'" for c in new_crns)
    op.execute(sa.text(f"DELETE FROM sections WHERE section_number IN ({crn_list})"))

    new_codes = [
        'CMPS 202','CMPS 208','CMPS 211','CMPS 214','CMPS 215','CMPS 221',
        'CMPS 224','CMPS 231','CMPS 232','CMPS 240','CMPS 241','CMPS 242',
        'CMPS 243','CMPS 244','CMPS 261','CMPS 262','CMPS 271','CMPS 279',
        'CMPS 288','CMPS 297AF','CMPS 297U','CMPS 297Z',
        'CMPS 299','CMPS 299A','CMPS 299B',
        'CMPS 302','CMPS 324','CMPS 332','CMPS 351','CMPS 395A','CMPS 396AK',
        'CMPS 398','CMPS 399','CMPS 399A','CMPS 399B','CMPS 399C',
    ]
    code_list = ', '.join(f"'{c}'" for c in new_codes)
    op.execute(sa.text(f"DELETE FROM courses WHERE code IN ({code_list})"))

    new_prof_ids = [
        '00000000-0000-4000-8000-000000000001',
        '00000000-0000-4000-8000-000000000002',
        '00000000-0000-4000-8000-000000000003',
        '00000000-0000-4000-8000-000000000004',
        '00000000-0000-4000-8000-000000000005',
        '00000000-0000-4000-8000-000000000006',
        '00000000-0000-4000-8000-000000000007',
        '00000000-0000-4000-8000-000000000008',
        '00000000-0000-4000-8000-000000000009',
        '00000000-0000-4000-8000-000000000010',
        '00000000-0000-4000-8000-000000000011',
        '00000000-0000-4000-8000-000000000012',
        '00000000-0000-4000-8000-000000000013',
        '00000000-0000-4000-8000-000000000014',
        '00000000-0000-4000-8000-000000000015',
        '00000000-0000-4000-8000-000000000016',
        '00000000-0000-4000-8000-000000000017',
        '00000000-0000-4000-8000-000000000018',
        '00000000-0000-4000-8000-000000000019',
        '00000000-0000-4000-8000-000000000020',
        '00000000-0000-4000-8000-000000000021',
        '00000000-0000-4000-8000-000000000022',
        '00000000-0000-4000-8000-000000000023',
        '00000000-0000-4000-8000-000000000024',
        '00000000-0000-4000-8000-000000000025',
        '00000000-0000-4000-8000-000000000026',
        '00000000-0000-4000-8000-000000000027',
        '00000000-0000-4000-8000-000000000028',
        '00000000-0000-4000-8000-000000000029',
        '00000000-0000-4000-8000-000000000030',
        '00000000-0000-4000-8000-000000000031',
        '00000000-0000-4000-8000-000000000032',
        '00000000-0000-4000-8000-000000000033',
        '00000000-0000-4000-8000-000000000034',
        '00000000-0000-4000-8000-000000000035',
        '00000000-0000-4000-8000-000000000036',
        '00000000-0000-4000-8000-000000000037',
        '00000000-0000-4000-8000-000000000038',
        '00000000-0000-4000-8000-000000000039',
    ]
    pid_list = ', '.join(f"'{p}'" for p in new_prof_ids)
    op.execute(sa.text(f"DELETE FROM professors WHERE id IN ({pid_list})"))
