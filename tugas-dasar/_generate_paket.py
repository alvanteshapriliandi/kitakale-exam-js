#!/usr/bin/env python3
"""Generate paket B additions and paket C–O. Deleted after the HTML is written."""

import re
from pathlib import Path

DIR = Path(__file__).resolve().parent
KET = {
    "var": "Ketentuan proses: Simpan data awal yang ada pada cerita. Lakukan setiap perubahan secara berurutan, lalu tampilkan kondisi akhirnya. Nilai akhir tidak boleh ditulis langsung.",
    "arith": "Ketentuan proses: Simpan seluruh angka pada cerita, lakukan semua operasi hitung dari data tersebut, lalu tampilkan hasil akhir. Nilai hasil tidak boleh ditulis langsung.",
    "cmp": "Ketentuan proses: Simpan angka yang dibandingkan, hasilkan nilai boolean dengan operator perbandingan, lalu tampilkan hasilnya. Jangan memakai percabangan. Nilai true atau false tidak boleh ditulis langsung.",
    "cmp_str": "Ketentuan proses: Simpan kedua data, hasilkan nilai boolean dengan operator perbandingan, lalu tampilkan hasilnya. Jangan memakai percabangan. Nilai true atau false tidak boleh ditulis langsung.",
    "logic": "Ketentuan proses: Simpan data syarat, gabungkan dengan operator logika, lalu tampilkan hasil booleannya. Jangan memakai percabangan. Nilai true atau false tidak boleh ditulis langsung.",
    "not": "Ketentuan proses: Simpan data syarat, balik nilainya dengan operator logika, lalu tampilkan hasil booleannya. Jangan memakai percabangan. Nilai true atau false tidak boleh ditulis langsung.",
    "ife": "Ketentuan proses: Simpan data yang menentukan hasil, periksa kondisi dengan if dan else, lalu tampilkan pesannya. Pesan akhir tidak boleh ditulis langsung.",
    "cat": "Ketentuan proses: Simpan data yang menentukan kategori, periksa batas kondisi dengan if, else if, dan else, lalu tampilkan hasilnya. Kategori akhir tidak boleh ditulis langsung.",
    "code": "Ketentuan proses: Simpan kode pilihan, tentukan hasil dengan if, else if, dan else, lalu tampilkan hasilnya. Nama hasil tidak boleh ditulis langsung.",
    "cap": "Ketentuan proses: Simpan seluruh data pada cerita, hitung subtotal, tentukan biaya tambahan dengan if dan else, lalu tentukan kategori dengan if, else if, dan else. Nilai hasil dan kategori tidak boleh ditulis langsung.",
}


def tf(flag):
    return "true" if flag else "false"


def rp(n):
    return "Rp" + f"{n:,}".replace(",", ".")


def cmp_op(op, a, b):
    return {
        ">=": a >= b,
        "<=": a <= b,
        ">": a > b,
        "<": a < b,
    }[op]


def q(kind, text, output):
    assert text.strip().endswith(".")
    assert output.strip()
    for line in output.splitlines():
        assert line.strip()
        assert "None" not in line
    return {"kind": kind, "text": text.strip(), "output": output.strip()}


def build_var(s):
    a, b, flag = s["a"], s["b"], s["flag"]
    for field, delta in s["ops"]:
        assert str(abs(delta)) in s["ubah"], s["ubah"]
        if field == "a":
            a += delta
        elif field == "b":
            b += delta
        else:
            raise AssertionError(field)
    assert a >= 0 and b >= 0
    text = (
        f'{s["intro"]}, {s["a_label"]} {s["a"]}{s.get("a_suf", "")}, '
        f'{s["b_label"]} {s["b"]}{s.get("b_suf", "")}, dan status {s["flag_label"]} '
        f'<code>{tf(s["flag"])}</code>. {s["ubah"]} {s["tutup"]}'
    )
    lines = [
        f'{s["out_name"]}: {s["name"]}',
        f'{s["out_a"]}: {a}{s.get("out_a_suf", "")}',
        f'{s["out_b"]}: {b}{s.get("out_b_suf", "")}',
        f'{s["out_flag"]}: {tf(flag)}',
    ]
    return q("var", text, "\n".join(lines))


def build_shop(s):
    biaya = s["a"] * s["pa"]
    total = biaya + s["b"] * s["pb"]
    sisa = s["fund"] - total
    assert sisa > 0
    text = (
        f'{s["who"]} {s["a"]} {s["a_name"]} seharga {rp(s["pa"])} per {s["unit"]} '
        f'dan {s["b"]} {s["b_name"]} seharga {rp(s["pb"])} per {s["unit"]}. '
        f'Dana yang disiapkan {rp(s["fund"])}. Tampilkan biaya {s["a_name"]}, total belanja, dan sisa dana.'
    )
    output = f'Biaya {s["out_a"]}: Rp{biaya}\nTotal Belanja: Rp{total}\nSisa Dana: Rp{sisa}'
    return q("arith", text, output)


def build_area(s):
    if s["shape"] == "rect":
        luas = s["p"] * s["l"]
        bentuk = (
            f'{s["benda"]} berbentuk persegi panjang, panjangnya {s["p"]} m dan lebarnya {s["l"]} m.'
        )
    else:
        luas = s["s"] * s["s"]
        bentuk = f'{s["benda"]} berbentuk persegi dengan sisi {s["s"]} m.'
    jumlah = luas // s["cover"]
    assert luas % s["cover"] == 0 and jumlah > 0
    text = (
        f'{bentuk} Satu {s["unit"]} menutup {s["cover"]} m². '
        f'Tampilkan luas {s["story"]} dan jumlah {s["unit_out"]}.'
    )
    output = f'{s["out_luas"]}: {luas} m²\n{s["out_n"]}: {jumlah}'
    return q("arith", text, output)


def build_vol(s):
    if s["shape"] == "cube":
        vol = s["s"] ** 3
        bentuk = f'{s["benda"]} berbentuk kubus dengan sisi {s["s"]} cm.'
    else:
        vol = s["p"] * s["l"] * s["t"]
        bentuk = (
            f'{s["benda"]} berbentuk balok, panjangnya {s["p"]} cm, '
            f'lebarnya {s["l"]} cm, dan tingginya {s["t"]} cm.'
        )
    jumlah = vol // s["unit"]
    assert vol % s["unit"] == 0 and jumlah > 0
    text = (
        f'{bentuk} Setiap {s["isi"]} memerlukan ruang {s["unit"]} cm³. '
        f'Tampilkan volume {s["story"]} dan banyak {s["isi"]} yang dapat dimuat.'
    )
    output = f'{s["out_v"]}: {vol} cm³\n{s["out_n"]}: {jumlah}'
    return q("arith", text, output)


def build_mod(s):
    per = s["n"] // s["k"]
    rem = s["n"] % s["k"]
    used = per * s["k"]
    assert rem != 0 and per > 0
    text = (
        f'{s["who"]} punya {s["n"]} {s["item"]} untuk dibagikan sama banyak kepada {s["k"]} {s["grup"]}. '
        f'Hasil bagi tiap {s["satuan"]} harus bilangan bulat. Tampilkan {s["item"]} yang diterima tiap {s["satuan"]}, '
        f'banyak {s["item"]} yang terbagi, dan sisa {s["item"]}.'
    )
    output = f'{s["out_per"]}: {per}\n{s["out_used"]}: {used}\n{s["out_rem"]}: {rem}'
    return q("arith", text, output)


def build_cmp(s):
    tipe = s["type"]
    if tipe == "min":
        ok = s["nilai"] >= s["batas"]
        under = s["nilai"] < s["batas"]
        text = (
            f'{s["kalimat"]} Tampilkan apakah {s["hal"]} sudah mencapai {s["batas_nama"]} '
            f'dan apakah {s["hal"]} masih di bawah {s["batas_nama"]}.'
        )
        output = f'{s["l_ok"]}: {tf(ok)}\n{s["l_under"]}: {tf(under)}'
        return q("cmp", text, output)
    if tipe == "str":
        same = s["benar"] == s["ketik"]
        text = (
            f'{s["apa"]} yang benar adalah <code>{s["benar"]}</code>. '
            f'Yang dimasukkan hari ini <code>{s["ketik"]}</code>. '
            f'Tampilkan apakah sama dan apakah berbeda.'
        )
        output = f'{s["l_same"]}: {tf(same)}\n{s["l_diff"]}: {tf(not same)}'
        return q("cmp_str", text, output)
    if tipe == "two":
        b1 = cmp_op(s["op1"], s["nilai"], s["b1"])
        b2 = cmp_op(s["op2"], s["nilai"], s["b2"])
        text = s["kalimat"]
        assert "Tampilkan" in text
        output = f'{s["l1"]}: {tf(b1)}\n{s["l2"]}: {tf(b2)}'
        return q("cmp", text, output)
    if tipe == "range":
        bmin = s["nilai"] >= s["lo"]
        bmax = s["nilai"] <= s["hi"]
        text = (
            f'{s["kalimat"]} Tampilkan apakah memenuhi batas minimal dan apakah masih dalam batas maksimal.'
        )
        output = f'{s["lmin"]}: {tf(bmin)}\n{s["lmax"]}: {tf(bmax)}'
        return q("cmp", text, output)
    raise AssertionError(tipe)


def build_and(s):
    angka = s["nilai"] >= s["batas"]
    hasil = angka and s["flag"]
    text = (
        f'{s["hasil"]} jika {s["syarat_angka"]} dan {s["syarat_bool"]}. '
        f'{s["angka_nama"]} hari ini {s["nilai"]}, sedangkan {s["flag_nama"]} bernilai <code>{tf(s["flag"])}</code>. '
        f'Tampilkan hasil syarat angka, status {s["flag_nama"]}, dan hasil gabungannya.'
    )
    output = (
        f'{s["l_angka"]}: {tf(angka)}\n{s["l_flag"]}: {tf(s["flag"])}\n{s["l_hasil"]}: {tf(hasil)}'
    )
    return q("logic", text, output)


def build_or(s):
    hasil = s["a"] or s["b"]
    text = (
        f'{s["hasil"]} jika {s["nama_a"]} atau {s["nama_b"]}. '
        f'{s["kalimat_a"]} bernilai <code>{tf(s["a"])}</code> dan {s["kalimat_b"]} bernilai <code>{tf(s["b"])}</code>. '
        f'Tampilkan kedua data dan hasil gabungannya.'
    )
    output = f'{s["la"]}: {tf(s["a"])}\n{s["lb"]}: {tf(s["b"])}\n{s["lh"]}: {tf(hasil)}'
    return q("logic", text, output)


def build_not(s):
    text = (
        f'{s["nama"]} bernilai <code>{tf(s["flag"])}</code>. '
        f'Tampilkan status itu dan kebalikannya sebagai {s["lawan"]}.'
    )
    output = f'{s["l1"]}: {tf(s["flag"])}\n{s["l2"]}: {tf(not s["flag"])}'
    return q("not", text, output)


def build_combo(s):
    utama = (s["nilai"] >= s["batas"]) and s["fa"]
    hasil = utama or s["fb"]
    text = (
        f'{s["hasil"]} jika {s["syarat_and"]}, atau jika {s["syarat_or"]}. '
        f'{s["angka"]} hari ini {s["nilai"]}, {s["nama_fa"]} bernilai <code>{tf(s["fa"])}</code>, '
        f'dan {s["nama_fb"]} bernilai <code>{tf(s["fb"])}</code>. '
        f'Tampilkan hasil syarat utama dan hasil keputusannya.'
    )
    output = f'Syarat Utama: {tf(utama)}\n{s["lhasil"]}: {tf(hasil)}'
    return q("logic", text, output)


def build_ife(s):
    ok = cmp_op(s["op"], s["nilai"], s["batas"])
    kata = "minimal" if s["op"] == ">=" else "maksimal"
    pesan = s["ya"] if ok else s["tidak"]
    noun = s["noun"]
    text = (
        f'{noun} adalah {s["nilai"]} {s["unit"]}. Jika {s["hal"]} {kata} {s["batas"]} {s["unit"]}, '
        f'tampilkan <code>{s["ya"]}</code>. Jika tidak, tampilkan <code>{s["tidak"]}</code>.'
    )
    return q("ife", text, f'{s["out"]}: {pesan}')


def build_cat(s):
    assert s["hi"] > s["mid"]
    if s["nilai"] >= s["hi"]:
        hasil = s["nh"]
    elif s["nilai"] >= s["mid"]:
        hasil = s["nm"]
    else:
        hasil = s["nl"]
    text = (
        f'{s["noun"]} adalah {s["nilai"]}. Jika minimal {s["hi"]}, statusnya <code>{s["nh"]}</code>. '
        f'Jika minimal {s["mid"]}, statusnya <code>{s["nm"]}</code>. Selain itu, statusnya <code>{s["nl"]}</code>. '
        f'Tampilkan status hari ini.'
    )
    return q("cat", text, f'{s["out"]}: {hasil}')


def build_code(s):
    mapping = s["maps"]
    chosen = s["chosen"]
    found = dict(mapping).get(chosen, s["lain"])
    a, b, c = mapping
    text = (
        f'Kode {s["apa"]} <code>{a[0]}</code> berarti {a[1]}, <code>{b[0]}</code> berarti {b[1]}, '
        f'dan <code>{c[0]}</code> berarti {c[1]}. Kode lain berarti <code>{s["lain"]}</code>. '
        f'Kode hari ini <code>{chosen}</code>. Tampilkan namanya.'
    )
    return q("code", text, f'{s["out"]}: {found}')


def build_cap(s):
    sub = s["qty"] * s["price"]
    apply = s["ukur"] > s["batas"]
    total = sub + (s["fee"] if apply else 0)
    alt = sub + (0 if apply else s["fee"])

    def band(v):
        if v >= s["hi"]:
            return "H"
        if v >= s["mid"]:
            return "M"
        return "L"

    assert s["hi"] > s["mid"]
    assert band(total) != band(alt), (s["item"], sub, total, alt)
    if band(total) == "H":
        cat = s["nh"]
    elif band(total) == "M":
        cat = s["nm"]
    else:
        cat = s["nl"]
    satuan = s.get("satuan", "")
    text = (
        f'{s["who"]} {s["qty"]} {s["item"]} seharga {rp(s["price"])} per {s["unit"]}. '
        f'Biaya {s["fee_nama"]} {rp(s["fee"])} ditambahkan hanya jika {s["hal"]} lebih dari {s["batas"]}{satuan}. '
        f'{s["hal"][:1].upper() + s["hal"][1:]} hari ini {s["ukur"]}{satuan}. '
        f'Setelah total dihitung, kategori <code>{s["nh"]}</code> bila total minimal {rp(s["hi"])}, '
        f'<code>{s["nm"]}</code> bila minimal {rp(s["mid"])}, selain itu <code>{s["nl"]}</code>. '
        f'Tampilkan subtotal, total bayar, dan kategori.'
    )
    output = f'Subtotal: Rp{sub}\nTotal Bayar: Rp{total}\nKategori: {cat}'
    return q("cap", text, output)


def build_packet(spec):
    builders = {
        "vars": build_var,
        "shop": build_shop,
        "area": build_area,
        "vol": build_vol,
        "mod": build_mod,
        "cmps": build_cmp,
        "ands": build_and,
        "ors": build_or,
        "nots": build_not,
        "combo": build_combo,
        "ife": build_ife,
        "cat": build_cat,
        "code": build_code,
        "cap": build_cap,
    }
    order = ["vars", "vars", "vars", "vars", "shop", "area", "vol", "mod", "cmps", "cmps", "cmps", "cmps", "ands", "ors", "nots", "combo", "ife", "cat", "code", "cap"]
    indexes = {key: 0 for key in builders}
    questions = []
    for key in order:
        item = spec[key]
        if isinstance(item, list):
            data = item[indexes[key]]
            indexes[key] += 1
        else:
            data = item
        try:
            questions.append(builders[key](data))
        except Exception as exc:
            raise RuntimeError(f'Paket {spec["letter"]} {key} #{indexes[key]}: {exc}') from exc
    assert len(questions) == 20
    texts = [item["text"] for item in questions]
    assert len(set(texts)) == 20
    return questions


def article(n, item):
    ket_key = {
        "var": "var",
        "arith": "arith",
        "cmp": "cmp",
        "cmp_str": "cmp_str",
        "logic": "logic",
        "not": "not",
        "ife": "ife",
        "cat": "cat",
        "code": "code",
        "cap": "cap",
    }[item["kind"]]
    text = f'{item["text"]}  {KET[ket_key]}'
    return (
        '                <article class="question-card">\n'
        f'                    <h3>{n:02d}</h3>\n'
        f'                    <p class="question-text">{text}</p>\n'
        '                    <p class="output-label">\n'
        '                        <strong>Output yang Diharapkan:</strong>\n'
        '                    </p>\n'
        f'                    <pre><code class="language-text">{item["output"]}\n'
        '</code></pre>\n'
        '                </article>'
    )


def render(letter, questions):
    body = "\n".join(article(i, item) for i, item in enumerate(questions, 1))
    return f'''<!DOCTYPE html>
<html lang="id">
    <head>
        <meta charset="utf-8" />
        <meta content="width=device-width, initial-scale=1.0" name="viewport" />
        <title>Ujian Dasar JavaScript: Variabel, Operator, dan Percabangan — Paket {letter}</title>
        <link rel="stylesheet" href="../kitakale-latihan.css" />
    </head>
    <body id="preview">
        <main class="page-shell">
            <header class="brand-bar">
                <div class="brand-name">
                    <span class="brand-mark">&lt;/&gt;</span>
                    <span>Kitakale Coding Lab</span>
                </div>
                <span class="brand-tag">UJIAN • JAVASCRIPT</span>
            </header>
            <section class="hero">
                <h1>Ujian Dasar JavaScript — Variabel, Operator, dan Percabangan (Paket {letter})</h1>
                <p class="topic">
                    <strong>Topik:</strong> Variabel • Operator Aritmatika • Operator Perbandingan • Operator Logika • Percabangan (if, else, else if)
                </p>
                <p class="instruction">
                    <strong>Petunjuk:</strong> Baca setiap soal cerita dengan teliti. Tentukan data yang dibutuhkan, lalu buat program JavaScript untuk menyelesaikan masalahnya. Materi soal hanya variabel, operator, dan percabangan.
                </p>
                <p class="instruction">
                    <strong>Ketentuan Pengerjaan:</strong> Nilai diberikan dari proses program, bukan hanya tampilan akhir. Simpan data awal dari cerita, lakukan proses yang diminta, lalu tampilkan hasil akhirnya. Jangan menulis nilai hasil atau pesan akhir secara langsung.
                </p>
            </section>
            <section aria-label="Daftar soal JavaScript" class="questions">
{body}
            </section>
            <footer class="site-footer">
                <span>Ujian Dasar JavaScript — <strong>Paket {letter}</strong></span>
                <span>Kitakale • Belajar Logika dari Dasar</span>
            </footer>
        </main>
    </body>
</html>
'''


def packet(**kwargs):
    return kwargs


def main():
    from _packets_data import PACKETS

    letters = [spec["letter"] for spec in PACKETS]
    assert letters == list("BCDEFGHIJKLMNO"), letters

    seen_texts = set()
    for spec in PACKETS:
        questions = build_packet(spec)
        for item in questions:
            key = item["text"]
            assert key not in seen_texts, f'Duplikat cerita di paket {spec["letter"]}: {key[:80]}'
            seen_texts.add(key)
        path = DIR / f'Ujian_Dasar_JavaScript__Variabel_Operator_Percabangan_Paket_{spec["letter"]}.html'
        path.write_text(render(spec["letter"], questions), encoding="utf-8")
        print(f'wrote {path.name} ({len(questions)} soal)')

    print(f'done: {len(PACKETS)} paket, {len(seen_texts)} soal unik')


if __name__ == "__main__":
    main()
