# -*- coding: utf-8 -*-

"""

mFk AcilNet - Profesyonel Yerel Test ve Önizleme Sunucusu

Tüm rotaları (Kütüphane, Harita, Yönetim, Arama, Okuyucu) dinamik ve çalışan simülasyonlarla sunar.

"""

import http.server

import socketserver

import os

import sys

import webbrowser

import threading

import time

import urllib.parse

import json

PORT = 8080
VOICE_DISPATCHES = []
VOICE_CHANNELS_BUSY = {}
TEXT_MESSAGES = [{'cat': 'duyuru', 'text': 'mFk AcilNet İstasyonu aktif. Çevrimdışı yerel Wi-Fi ağı üzerinden kesintisiz çalışmaktadır.'}]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WWW_HOME = os.path.join(BASE_DIR, "www", "home")

SAMPLE_CATALOG_XML = """<?xml version="1.0" encoding="UTF-8"?>

<feed xmlns="http://www.w3.org/2005/Atom">

  <title>mFk AcilNet Tam Çevrimdışı Kiwix Kataloğu</title>

  

  <entry>

    <title>Vikipedi (Türkçe)</title>

    <link type="text/html" href="/kiwix/wikipedia_tr_all_maxi_2024-05" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/wikipedia/wikipedia_tr_all_maxi_2024-05.zim.meta4" length="9663676416" />

  </entry>

  <entry>

    <title>Wikipedia (English)</title>

    <link type="text/html" href="/kiwix/wikipedia_en_all_maxi_2024-05" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/wikipedia/wikipedia_en_all_maxi_2024-05.zim.meta4" length="128849018880" />

  </entry>

  <entry>

    <title>Vikisözlük</title>

    <link type="text/html" href="/kiwix/wiktionary_tr_all_nopic_2024-04" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/wiktionary/wiktionary_tr_all_nopic_2024-04.zim.meta4" length="849346560" />

  </entry>

  <entry>

    <title>iFixit (Türkçe)</title>

    <link type="text/html" href="/kiwix/ifixit_tr_all_2024-03" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/ifixit/ifixit_tr_all_2024-03.zim.meta4" length="3865470566" />

  </entry>

  <entry>

    <title>Vikikitap</title>

    <link type="text/html" href="/kiwix/wikibooks_tr_all_maxi_2024-04" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/wikibooks/wikibooks_tr_all_maxi_2024-04.zim.meta4" length="28311552" />

  </entry>

  <entry>

    <title>Vikikaynak</title>

    <link type="text/html" href="/kiwix/wikisource_tr_all_maxi_2024-04" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/wikisource/wikisource_tr_all_maxi_2024-04.zim.meta4" length="71303168" />

  </entry>

  <entry>

    <title>PhET Simülasyonları</title>

    <link type="text/html" href="/kiwix/phet_tr_all_2024-01" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/phet/phet_tr_all_2024-01.zim.meta4" length="112197632" />

  </entry>

  <entry>

    <title>WikiMed Tıp Ansiklopedisi</title>

    <link type="text/html" href="/kiwix/wikipedia_en_medicine_maxi_2024-06" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/wikipedia/wikipedia_en_medicine_maxi_2024-06.zim.meta4" length="2147483648" />

  </entry>

  <entry>

    <title>MDWiki Tıp Kütüphanesi</title>

    <link type="text/html" href="/kiwix/mdwiki_en_all_maxi_2024-02" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/other/mdwiki_en_all_maxi_2024-02.zim.meta4" length="2254857830" />

  </entry>

  <entry>

    <title>MedlinePlus Sağlık Bilgi Sistemi</title>

    <link type="text/html" href="/kiwix/medlineplus.gov_en_all_2024-05" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/zimit/medlineplus.gov_en_all_2024-05.zim.meta4" length="2040109465" />

  </entry>

  <entry>

    <title>Sahra Tıbbı El Kitabı</title>

    <link type="text/html" href="/kiwix/irp.fas.org_en_military-medicine_2024-01" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/zimit/irp.fas.org_en_military-medicine_2024-01.zim.meta4" length="68157440" />

  </entry>

  <entry>

    <title>Afet Sonrası Kütüphanesi</title>

    <link type="text/html" href="/kiwix/zimgit-post-disaster_en_2024-01" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/other/zimgit-post-disaster_en_2024-01.zim.meta4" length="644874240" />

  </entry>

  <entry>

    <title>İçme Suyu Dezenfeksiyonu</title>

    <link type="text/html" href="/kiwix/zimgit-water_en_2024-01" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/other/zimgit-water_en_2024-01.zim.meta4" length="20971520" />

  </entry>

  <entry>

    <title>Gıda Saklama ve Güvenliği</title>

    <link type="text/html" href="/kiwix/zimgit-food-preparation_en_2024-01" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/other/zimgit-food-preparation_en_2024-01.zim.meta4" length="97517568" />

  </entry>

  <entry>

    <title>Kurtarma Bağları &amp; Düğümler</title>

    <link type="text/html" href="/kiwix/zimgit-knots_en_2024-01" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/other/zimgit-knots_en_2024-01.zim.meta4" length="28311552" />

  </entry>

  <entry>

    <title>Ready.gov Resmi Eylem Planı</title>

    <link type="text/html" href="/kiwix/ready.gov_en_all_2024-04" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/zimit/ready.gov_en_all_2024-04.zim.meta4" length="2040109465" />

  </entry>

  <entry>

    <title>iFixit Teknik Onarım (EN)</title>

    <link type="text/html" href="/kiwix/ifixit_en_all_2024-03" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/ifixit/ifixit_en_all_2024-03.zim.meta4" length="3221225472" />

  </entry>

  <entry>

    <title>Low-tech Magazine</title>

    <link type="text/html" href="/kiwix/solar.lowtechmagazine.com_mul_all_2024-02" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/zimit/solar.lowtechmagazine.com_mul_all_2024-02.zim.meta4" length="702545920" />

  </entry>

  <entry>

    <title>Appropedia Kütüphanesi</title>

    <link type="text/html" href="/kiwix/appropedia_en_all_2024-03" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/other/appropedia_en_all_2024-03.zim.meta4" length="608174080" />

  </entry>

  <entry>

    <title>Amatör Telsizcilik (HAM)</title>

    <link type="text/html" href="/kiwix/ham.stackexchange.com_en_all_2024-01" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/stack_exchange/ham.stackexchange.com_en_all_2024-01.zim.meta4" length="314572800" />

  </entry>

  <entry>

    <title>WikiMed Türkçe</title>

    <link type="text/html" href="/kiwix/wikipedia_tr_medicine_maxi_2024-06" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/wikipedia/wikipedia_tr_medicine_maxi_2024-06.zim.meta4" length="786432000" />

  </entry>

  <entry>

    <title>Electronics Stack Exchange</title>

    <link type="text/html" href="/kiwix/electronics.stackexchange.com_en_all_2024-03" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/stack_exchange/electronics.stackexchange.com_en_all_2024-03.zim.meta4" length="1288490188" />

  </entry>

  <entry>

    <title>Unix &amp; Linux Sistem Yönetimi</title>

    <link type="text/html" href="/kiwix/unix.stackexchange.com_en_all_2024-04" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/stack_exchange/unix.stackexchange.com_en_all_2024-04.zim.meta4" length="2254857830" />

  </entry>

  <entry>

    <title>Open Source Ecology</title>

    <link type="text/html" href="/kiwix/opensourceecology_en_all_2024-01" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/other/opensourceecology_en_all_2024-01.zim.meta4" length="838860800" />

  </entry>

  <entry>

    <title>HazMat Kimyasal Güvenlik (ERG)</title>

    <link type="text/html" href="/kiwix/chemm.nlm.nih.gov_en_all_2024-02" />

    <link rel="http://opds-spec.org/acquisition/open-access" type="application/x-zim" href="https://download.kiwix.org/zim/zimit/chemm.nlm.nih.gov_en_all_2024-02.zim.meta4" length="188743680" />

  </entry>

</feed>

"""

HTML_LAYOUT_WRAPPER = """<!doctype html>

<html lang="tr">

<head>

<meta charset="utf-8">

<meta name="viewport" content="width=device-width, initial-scale=1">

<title>{title} - mFk AcilNet İstasyonu</title>

<style>

  body {{ background: #090d16; color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 0; padding: 24px; line-height: 1.6; }}

  .nav {{ display: flex; align-items: center; justify-content: space-between; border-bottom: 1px solid #1e293b; padding-bottom: 16px; margin-bottom: 24px; }}

  .btn {{ background: #1e293b; border: 1px solid #334155; color: #f8fafc; padding: 8px 14px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 13px; display: inline-flex; align-items: center; gap: 6px; }}

  .btn:hover {{ background: #334155; border-color: #00e5ff; }}

  .card {{ background: rgba(30, 41, 59, 0.7); border: 1px solid #334155; border-radius: 14px; padding: 24px; margin-bottom: 20px; }}

  h1 {{ font-size: 22px; font-weight: 800; margin: 0 0 8px; color: #00e5ff; }}

  p {{ color: #94a3b8; font-size: 14px; margin: 0 0 16px; }}

  .badge {{ background: rgba(0, 229, 255, 0.15); color: #00e5ff; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: 700; }}

</style>

</head>

<body>

<div style="max-width: 1000px; margin: 0 auto;">

  <div class="nav">

    <a href="/home" class="btn">&larr; Ana Ekrana Dön</a>

    <span style="font-size: 12px; color: #64748b; font-weight: 700;">mFk AcilNet Çevrimdışı Servis Modülü</span>

  </div>

  {content}

</div>

</body>

</html>"""

def make_kiwix_page():

    content = """

    <div class="card">

      <span class="badge">KIWIX OFFLINE ENGINE</span>

      <h1 style="margin-top:12px;">Çevrimdışı Kütüphane Sunucusu</h1>

      <p>Bu ekran, Raspberry Pi / donanım üzerindeki Kiwix ZIM okuyucu motorunun simülasyonudur. İndirilen tüm ansiklopedi ve kitaplar burada yer alır.</p>

      

      <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 14px; margin-top: 20px;">

        <div style="background:#0f172a; border:1px solid #334155; padding:16px; border-radius:10px;">

          <h3 style="font-size:15px; margin:0 0 6px;">Vikipedi (Türkçe) Maxi</h3>

          <p style="font-size:12px; margin:0 0 10px;">500.000+ resimli Türkçe makale arşivi.</p>

          <a href="/kiwix/wikipedia_tr_all_maxi_2024-05" class="btn" style="color:#00e5ff;">Makaleleri Oku &rarr;</a>

        </div>

        <div style="background:#0f172a; border:1px solid #334155; padding:16px; border-radius:10px;">

          <h3 style="font-size:15px; margin:0 0 6px;">iFixit Türkçe Tamir Kılavuzu</h3>

          <p style="font-size:12px; margin:0 0 10px;">Cihaz, tesisat ve motor tamir rehberleri.</p>

          <a href="/kiwix/ifixit_tr_all_2024-03" class="btn" style="color:#00e5ff;">Kılavuzları Oku &rarr;</a>

        </div>

        <div style="background:#0f172a; border:1px solid #334155; padding:16px; border-radius:10px;">

          <h3 style="font-size:15px; margin:0 0 6px;">WikiMed Acil Tıp Ansiklopedisi</h3>

          <p style="font-size:12px; margin:0 0 10px;">Klinik sağlık, ilk yardım ve ameliyat rehberi.</p>

          <a href="/kiwix/wikipedia_en_medicine_maxi_2024-06" class="btn" style="color:#00e5ff;">İncele &rarr;</a>

        </div>

      </div>

    </div>

    """

    return HTML_LAYOUT_WRAPPER.format(title="Kiwix Kütüphanesi", content=content)

def make_reader_page(book_id):

    b_lower = book_id.lower()

    

    # 1. Tıp & İlk Yardım

    if 'medicine' in b_lower or 'mdwiki' in b_lower or 'medline' in b_lower:

        topic_title = "WikiMed Acil Tıp ve Klinik İlk Yardım"

        article_body = """

        <h2 style="color:#38bdf8; font-size:16px;">Acil Durum Kanama Kontrolü ve Turnike (CAT) Protokolü</h2>

        <p>Atardamar kanamalarında fışkıran kan dakikalar içinde hipovolemik şoka yol açar. Yaranın 5-7 cm yukarısına kemik üzerine turnike uygulanmalı, kanama durana kadar sıkılmalı ve uygulandığı dakika silinmez kalemle alına yazılmalıdır.</p>

        <div style="background:#0f172a; padding:12px; border-radius:6px; border:1px solid #1e293b; margin:10px 0;">

          <h3 style="font-size:13px; color:#f87171; margin-top:0;">CPR (Kalp Masajı) Hayat Kurtarma Döngüsü</h3>

          <p>Yetişkinde dakikada 100-120 bası ritminde, göğüs kemiğini 5-6 cm çökertecek şekilde 30 göğüs basısı ve 2 suni solunum uygulanır. Ağızdan solunum engeli varsa yalnızca kesintisiz göğüs masajına devam edilir.</p>

        </div>

        <div style="margin-top:14px;"><a href="/home/tip.html" class="btn" style="color:#38bdf8;">Kapsamlı Türkçe Tıp Kütüphanesini Aç &rarr;</a></div>

        """

    # 2. Su ve Hayatta Kalma

    elif 'water' in b_lower or 'disaster' in b_lower or 'food' in b_lower or 'knot' in b_lower:

        topic_title = "Afet Koşullarında Su Arıtma ve Hayatta Kalma"

        article_body = """

        <h2 style="color:#38bdf8; font-size:16px;">Şebekesiz Su Dezenfeksiyonu ve Filtreleme</h2>

        <p>Bulanık sular önce kumaş/tülbentten süzülür. 1 litre berrak suya 2 damla kokusuz çamaşır suyu (%5-6 sodyum hipoklorit) damlatılıp 30 dakika bekletilir. Kaynatma yöntemi için su en az 1 dakika fokurdayacak şekilde kaynatılmalıdır.</p>

        <div style="background:#0f172a; padding:12px; border-radius:6px; border:1px solid #1e293b; margin:10px 0;">

          <h3 style="font-size:13px; color:#38bdf8; margin-top:0;">Temel Kurtarma Düğümleri</h3>

          <p><b>Sekizli Bağı:</b> Yük taşıma ve emniyet ipi kasası.<br><b>Kazık Bağı:</b> Direğe veya ağaca çadır ve branda sabitleme.<br><b>Camadan Bağı:</b> İki ipi veya sargı bezini birbirine ekleme.</p>

        </div>

        <div style="margin-top:14px;"><a href="/home/su-gida.html" class="btn" style="color:#38bdf8;">Kapsamlı Su ve Gıda Rehberini Aç &rarr;</a></div>

        """

    # 3. Elektronik ve Solar

    elif 'electron' in b_lower or 'solar' in b_lower or 'lowtech' in b_lower:

        topic_title = "Off-Grid Güneş Paneli, Akü ve Elektronik Devreler"

        article_body = """

        <h2 style="color:#38bdf8; font-size:16px;">12V Güneş Paneli ve Akü Bağlantı Sırası</h2>

        <p>Şarj kontrol cihazına (MPPT/PWM) <b>ÖNCE AKÜ</b>, ardından <b>İKİNCİ OLARAK GÜNEŞ PANELİ</b> bağlanmalıdır. Panel önce bağlanırsa regülatörün voltaj tespit devresi yanar.</p>

        <div style="background:#0f172a; padding:12px; border-radius:6px; border:1px solid #1e293b; margin:10px 0;">

          <h3 style="font-size:13px; color:#38bdf8; margin-top:0;">18650 Lityum Batarya Güvenliği</h3>

          <p>Hücre voltajı 2.8V altına düşürülmemeli, 4.2V üzerine çıkarılmamalıdır. Seri bağlı hücrelerde termal kaçak ve yangın riskini önlemek için BMS (Battery Management System) devresi şarttır.</p>

        </div>

        <div style="margin-top:14px;"><a href="/home/solar.html" class="btn" style="color:#38bdf8;">Elektronik ve Solar Şemaları Aç &rarr;</a></div>

        """

    # 4. Kimyasal / Biyolojik Güvenlik

    elif 'chem' in b_lower or 'hazmat' in b_lower:

        topic_title = "HazMat Tehlikeli Kimyasal Maddeler & Acil Müdahale"

        article_body = """

        <h2 style="color:#f87171; font-size:16px;">Klor ve Amonyak Gaz Sızıntısı Tahliye Protokolü</h2>

        <p>Klor gazı havadan ağırdır ve çukurlara çöker (üst katlara kaçılmalıdır). Amonyak gazı havadan hafiftir ve yukarı yükselir. Rüzgar yönü tespit edilerek rüzgar arkaya alınmalı ve en az 800 metre uzağa tahliye olunmalıdır.</p>

        <div style="margin-top:14px;"><a href="/home/hazmat.html" class="btn" style="color:#f87171;">Kimyasal Güvenlik Rehberini Aç &rarr;</a></div>

        """

    # 5. Genel Vikipedi & Diğerleri

    else:

        topic_title = f"{book_id} - Çevrimdışı Ansiklopedi"

        article_body = f"""

        <h2 style="color:#38bdf8; font-size:16px;">Çevrimdışı Kütüphane Arşivi Devrede</h2>

        <p>Bu kaynak, internet bağlantısı olmaksızın yerel istasyon belleğinden tam metin ve görselleriyle sunulmaktadır. İlgili başlıklara, arama terimlerine ve indekslere sol menüden veya genel aramadan erişebilirsiniz.</p>

        <div style="display:flex; gap:8px; margin-top:12px;">

          <a href="/home/acil.html" class="btn" style="color:#f87171;">112 Acil Protokolü</a>

          <a href="/home/harita.html" class="btn" style="color:#38bdf8;">Çevrimdışı Harita</a>

          <a href="/home/tip.html" class="btn" style="color:#34d399;">Klinik İlk Yardım</a>

        </div>

        """

    content = f"""

    <div class="card">

      <span class="badge">OFFLINE KNOWLEDGE DATABASE</span>

      <h1 style="margin-top:12px;">{topic_title}</h1>

      <p style="color:#94a3b8; font-size:12px;">Arşiv Kimliği: {book_id} &bull; İnternet Gerektirmez</p>

      

      <div style="background:#090d16; border:1px solid #1e293b; border-radius:8px; padding:18px; margin-top:14px; line-height:1.6;">

        {article_body}

      </div>

      <div style="margin-top:18px; display:flex; gap:8px;">

        <a href="/home" class="btn">&larr; Ana Ekrana Dön</a>

        <a href="/kiwix/" class="btn">Tüm ZIM Arşivleri</a>

      </div>

    </div>

    """

    return HTML_LAYOUT_WRAPPER.format(title=topic_title, content=content)

def make_maps_page():

    content = """

    <div class="card">

      <span class="badge">OFFLINE MAP SERVER</span>

      <h1 style="margin-top:12px;">OpenStreetMap Çevrimdışı Harita</h1>

      <p>OpenStreetMap vektör ve karo harita servisi devrede. İnternet olmadan sokak sokak konum ve rota incelemesi yapılabilir.</p>

      

      <div style="background:#0d1829; border:1px solid #334155; border-radius:12px; height:420px; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center; padding:20px; position:relative; overflow:hidden;">

        <div style="position:absolute; inset:0; opacity:0.15; background: repeating-linear-gradient(0deg, #00e5ff, #00e5ff 1px, transparent 1px, transparent 40px), repeating-linear-gradient(90deg, #00e5ff, #00e5ff 1px, transparent 1px, transparent 40px);"></div>

        

        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#00e5ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom:16px; z-index:1;"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"></polygon><line x1="9" y1="3" x2="9" y2="18"></line><line x1="15" y1="6" x2="15" y2="21"></line></svg>

        <h2 style="font-size:18px; margin:0 0 8px; z-index:1;">Çevrimdışı Harita Karo Sunucusu Hazır</h2>

        <p style="max-width:500px; font-size:13px; z-index:1;">Raspberry Pi / Donanım üzerine indirilmiş 40 GB'lık OpenStreetMap veritabanı map-server üzerinden Leaflet ile sunulur.</p>

        <a href="/home" class="btn" style="margin-top:12px; z-index:1; color:#00e5ff;">&larr; Ana Ekrana Dön</a>

      </div>

    </div>

    """

    return HTML_LAYOUT_WRAPPER.format(title="Çevrimdışı Harita", content=content)

def make_admin_page():

    content = """

    <div class="card">

      <span class="badge">SYSTEM MANAGEMENT</span>

      <h1 style="margin-top:12px;">mFkWifi Yönetim Konsolu (Admin)</h1>

      <p>Cihaz durumu, bağlı kullanıcılar, Wi-Fi yapılandırması ve disk kontrolleri bu panelden yönetilir.</p>

      

      <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap:14px; margin:20px 0;">

        <div style="background:#0f172a; border:1px solid #334155; padding:16px; border-radius:10px;">

          <div style="font-size:12px; color:#94a3b8; font-weight:700;">WI-FI AP YAYINI</div>

          <div style="font-size:16px; font-weight:800; color:#10b981; margin:6px 0;">AKTİF (DataWifi)</div>

          <div style="font-size:12px; color:#64748b;">Kanal: 6 &bull; Şifre: Korumalı</div>

        </div>

        <div style="background:#0f172a; border:1px solid #334155; padding:16px; border-radius:10px;">

          <div style="font-size:12px; color:#94a3b8; font-weight:700;">BAĞLI CİHAZ SAYISI</div>

          <div style="font-size:16px; font-weight:800; color:#00e5ff; margin:6px 0;">3 İstemci</div>

          <div style="font-size:12px; color:#64748b;">IP Havuzu: 10.10.10.x</div>

        </div>

        <div style="background:#0f172a; border:1px solid #334155; padding:16px; border-radius:10px;">

          <div style="font-size:12px; color:#94a3b8; font-weight:700;">DONANIM SAĞLIĞI</div>

          <div style="font-size:16px; font-weight:800; color:#10b981; margin:6px 0;">MÜKEMMEL</div>

          <div style="font-size:12px; color:#64748b;">Voltaj: 5.0V &bull; Sıcaklık: 42°C</div>

        </div>

      </div>

      

      <div style="display:flex; gap:10px; margin-top:20px;">

        <a href="/home" class="btn" style="color:#00e5ff;">&larr; Ana Sayfaya Dön</a>

        <a href="/home/disk.json" class="btn" target="_blank">Sağlık JSON Çıktısı</a>

      </div>

    </div>

    """

    return HTML_LAYOUT_WRAPPER.format(title="Yönetim Paneli", content=content)

def make_kolibri_page():

    content = """

    <div class="card">

      <span class="badge">OFFLINE EDUCATION</span>

      <h1 style="margin-top:12px;">Kolibri Öğrenim Platformu</h1>

      <p>Khan Academy, MEB ve açık ders videolarının internetsiz sunulduğu eğitim modülüdür.</p>

      

      <div style="background:#0f172a; border:1px solid #334155; border-radius:12px; padding:30px; text-align:center;">

        <h3 style="font-size:17px; margin-bottom:8px;">Kolibri Sunucusu Hazır</h3>

        <p style="font-size:13px; max-width:500px; margin:0 auto 16px;">Donanımda Kolibri servisi (port 8008) çalıştığında öğrenci profilleri, matematik ve fen eğitim simülasyonları burada açılır.</p>

        <a href="/home" class="btn" style="color:#00e5ff;">&larr; Ana Menüye Dön</a>

      </div>

    </div>

    """

    return HTML_LAYOUT_WRAPPER.format(title="Kolibri Platformu", content=content)

def make_search_results(query):

    content = f"""

    <div class="card">

      <span class="badge">KIWIX FULL-TEXT SEARCH</span>

      <h1 style="margin-top:12px;">Arama Sonuçları: "{query}"</h1>

      <p>Kiwix kütüphanesi içindeki tüm makaleler ve başlıklar tarandı.</p>

      

      <div style="display:flex; flex-direction:column; gap:12px; margin-top:20px;">

        <div style="background:#0f172a; border:1px solid #334155; border-radius:8px; padding:16px;">

          <h3 style="font-size:15px; margin:0 0 4px; color:#00e5ff;">1. {query} - Vikipedi Maddesi</h3>

          <p style="font-size:13px; margin:0 0 8px;">Vikipedi Türkçe ansiklopedisinde '{query}' ile ilgili kapsamlı makale ve açıklamalar.</p>

          <a href="/kiwix/wikipedia_tr_all_maxi_2024-05" class="btn" style="font-size:12px;">Makaleyi Oku &rarr;</a>

        </div>

        <div style="background:#0f172a; border:1px solid #334155; border-radius:8px; padding:16px;">

          <h3 style="font-size:15px; margin:0 0 4px; color:#00e5ff;">2. {query} İlk Yardım ve Acil Müdahale</h3>

          <p style="font-size:13px; margin:0 0 8px;">WikiMed ve Sahra Tıbbı arşivinde '{query}' aramasıyla ilgili klinik talimatlar.</p>

          <a href="/kiwix/wikipedia_en_medicine_maxi_2024-06" class="btn" style="font-size:12px;">Tıp Rehberinde Oku &rarr;</a>

        </div>

      </div>

      

      <div style="margin-top:24px;">

        <a href="/home" class="btn" style="color:#00e5ff;">&larr; Ana Ekrana Dön</a>

      </div>

    </div>

    """

    return HTML_LAYOUT_WRAPPER.format(title=f"Arama: {query}", content=content)

class CustomHandler(http.server.SimpleHTTPRequestHandler):

    def translate_path(self, path):

        clean_path = path.split('?', 1)[0].split('#', 1)[0]

        # 1. Kök ve ana dizinler doğrudan www/home/index.html'e yönlendirilir

        if clean_path in ('/home', '/home/', '/'):

            return os.path.join(WWW_HOME, 'index.html')

            

        # 2. Eğer istek /home/ ile başlıyorsa www/home altından ara

        if clean_path.startswith('/home/'):

            rel_path = clean_path[len('/home/'):].lstrip('/')

            target = os.path.join(WWW_HOME, rel_path.replace('/', os.sep))

            if os.path.exists(target):

                return target

            return target

        # 3. /home olmadan doğrudan istenen dosya www/home içinde varsa oradan sun (Örn: /tip.html, /acil.html)

        rel_path = clean_path.lstrip('/')

        direct_target = os.path.join(WWW_HOME, rel_path.replace('/', os.sep))

        if os.path.exists(direct_target) and not os.path.isdir(direct_target):

            return direct_target

        # 4. Standart çalışma dizini

        return super().translate_path(path)

    def do_GET(self):

        parsed = urllib.parse.urlparse(self.path)

        path = parsed.path

        query_params = urllib.parse.parse_qs(parsed.query)

        # 1. Kiwix XML Kataloğu

        if path.startswith('/kiwix/catalog/'):

            self.send_response(200)

            self.send_header('Content-Type', 'application/xml; charset=utf-8')

            self.send_header('Access-Control-Allow-Origin', '*')

            self.end_headers()

            self.wfile.write(SAMPLE_CATALOG_XML.encode('utf-8'))

            return

        # 2. Kiwix Arama Servisi

        if path == '/kiwix/search':

            pattern = query_params.get('pattern', [''])[0]

            html = make_search_results(pattern or 'Genel Arama')

            self.send_response(200)

            self.send_header('Content-Type', 'text/html; charset=utf-8')

            self.end_headers()

            self.wfile.write(html.encode('utf-8'))

            return

        # 3. Kiwix Kütüphane Ana Sayfası

        if path == '/kiwix' or path == '/kiwix/':

            html = make_kiwix_page()

            self.send_response(200)

            self.send_header('Content-Type', 'text/html; charset=utf-8')

            self.end_headers()

            self.wfile.write(html.encode('utf-8'))

            return

        # 4. Kiwix Makale Okuyucu (Alt Rotalar)

        if path.startswith('/kiwix/'):

            book_id = path[len('/kiwix/'):].strip('/')

            html = make_reader_page(book_id)

            self.send_response(200)

            self.send_header('Content-Type', 'text/html; charset=utf-8')

            self.end_headers()

            self.wfile.write(html.encode('utf-8'))

            return

        # 5. Haritalar

        if path == '/maps' or path == '/maps/':

            harita_path = os.path.join(WWW_HOME, 'harita.html')

            if os.path.exists(harita_path):

                with open(harita_path, 'r', encoding='utf-8') as f:

                    html = f.read()

            else:

                html = make_maps_page()

            self.send_response(200)

            self.send_header('Content-Type', 'text/html; charset=utf-8')

            self.end_headers()

            self.wfile.write(html.encode('utf-8'))

            return

        # 6. Yönetim Konsolu (Admin)

        if path == '/admin' or path == '/admin/':

            html = make_admin_page()

            self.send_response(200)

            self.send_header('Content-Type', 'text/html; charset=utf-8')

            self.end_headers()

            self.wfile.write(html.encode('utf-8'))

            return

        # 7. Kolibri Eğitim Modülü

        if path == '/kolibri' or path == '/kolibri/':

            html = make_kolibri_page()

            self.send_response(200)

            self.send_header('Content-Type', 'text/html; charset=utf-8')

            self.end_headers()

            self.wfile.write(html.encode('utf-8'))

            return

                # Sesli Telsiz Durum ve Anons Listesi
        if path in ('/api/voice/list', '/api/voice/status'):
            now = time.time()
            # Süresi dolan mandalları temizle
            for ch in list(VOICE_CHANNELS_BUSY.keys()):
                if VOICE_CHANNELS_BUSY[ch]['expires'] <= now:
                    del VOICE_CHANNELS_BUSY[ch]
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            resp = {
                'busy': VOICE_CHANNELS_BUSY,
                'dispatches': VOICE_DISPATCHES[-20:]
            }
            self.wfile.write(json.dumps(resp).encode('utf-8'))
            return

        # 7.5. Yerel Yazılı Mesajlar
        if path == '/api/messages':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(TEXT_MESSAGES[:30]).encode('utf-8'))
            return

        # 8. Donanım Sağlık JSON

        if path in ('/home/disk.json', '/disk.json'):

            self.send_response(200)

            self.send_header('Content-Type', 'application/json; charset=utf-8')

            self.end_headers()

            self.wfile.write(b'{"checked":"2026-11-07T12:00:00Z","warnings":[]}')

            return

                # Favicon Servisi
        if path in ('/favicon.ico', '/favicon.svg', '/home/favicon.svg', '/home/favicon.ico'):
            fav_path = os.path.join(WWW_HOME, 'favicon.svg')
            if os.path.exists(fav_path):
                self.send_response(200)
                self.send_header('Content-Type', 'image/svg+xml')
                self.end_headers()
                with open(fav_path, 'rb') as fp:
                    self.wfile.write(fp.read())
                return

        # 9. Kök Dizin, /home ve Captive Portal Yönlendirmeleri
        if path in ('/', '/home', '/hotspot-detect.html', '/generate_204', '/gen_204', '/connecttest.txt', '/ncsi.txt'):

            self.send_response(302)

            self.send_header('Location', '/home/')

            self.end_headers()

            return

        # Standart Statik Dosya (index.html, acil.html vb.)

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length > 0 else b'{}'
        now = time.time()

        # Yerel Yazılı Mesaj Gönderimi
        if path == '/api/messages':
            try:
                data = json.loads(body.decode('utf-8'))
                author = str(data.get('author', '')).strip()[:30]
                text = str(data.get('text', '')).strip()[:300]
                cat = str(data.get('cat', 'duyuru')).strip()[:20]
                if text:
                    msg = {'cat': cat, 'text': text}
                    if author and author not in ('SİSTEM', 'ANONİM', 'DUYURU'):
                        msg['author'] = author
                    TEXT_MESSAGES.insert(0, msg)
                    if len(TEXT_MESSAGES) > 50:
                        TEXT_MESSAGES.pop()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            except Exception:
                self.send_response(400)
                self.end_headers()
            return

        # Mandal Basıldı - Kanal Meşguliyet Kilidi (Çakışma Önleme)
        if path == '/api/voice/busy':
            try:
                req = json.loads(body.decode('utf-8'))
                ch = str(req.get('channel', '1'))
                sender = req.get('sender', 'AFETZEDE')
                # Kanal kontrolü
                if ch in VOICE_CHANNELS_BUSY and VOICE_CHANNELS_BUSY[ch]['expires'] > now:
                    active = VOICE_CHANNELS_BUSY[ch]
                    if active['sender'] != sender:
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.send_header('Access-Control-Allow-Origin', '*')
                        self.end_headers()
                        self.wfile.write(json.dumps({'allowed': False, 'busy_by': active['sender']}).encode('utf-8'))
                        return
                # Kanalı bu kullanıcıya 30 saniyeliğine kilitle
                VOICE_CHANNELS_BUSY[ch] = {'sender': sender, 'expires': now + 30}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"allowed": true}')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
            return

        # Mandal Bırakıldı (Konuşma İptal / Tamamlandı) - Kilidi Boşa Çıkar
        if path == '/api/voice/release':
            try:
                req = json.loads(body.decode('utf-8'))
                ch = str(req.get('channel', '1'))
                sender = req.get('sender', '')
                if ch in VOICE_CHANNELS_BUSY:
                    if not sender or VOICE_CHANNELS_BUSY[ch].get('sender') == sender:
                        del VOICE_CHANNELS_BUSY[ch]
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"status":"released"}')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
            return

        # Ses Paketi Gönderildi - Mandalı Bırak
        if path == '/api/voice/send':
            try:
                data = json.loads(body.decode('utf-8'))
                data['id'] = int(time.time() * 1000)
                ch = str(data.get('channel', '1'))
                if ch in VOICE_CHANNELS_BUSY:
                    del VOICE_CHANNELS_BUSY[ch]
                VOICE_DISPATCHES.append(data)
                if len(VOICE_DISPATCHES) > 50:
                    VOICE_DISPATCHES.pop(0)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(b'{"status":"ok"}')
            except Exception as e:
                self.send_response(400)
                self.end_headers()
            return

        self.send_response(404)
        self.end_headers()

def start_server():

    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:

        print("=" * 60)

        print(f" mFk AcilNet Profesyonel Test Sunucusu Devrede!")

        print(f" Adres: http://127.0.0.1:{PORT}/home/")

        print(" Tum rotalar (/kiwix/, /maps, /admin, /kolibri vb.) aktiftir.")

        print("=" * 60)

        

        def open_browser():

            time.sleep(1)

            webbrowser.open(f"http://127.0.0.1:{PORT}/home/")

            

        threading.Thread(target=open_browser, daemon=True).start()

        

        try:

            httpd.serve_forever()

        except KeyboardInterrupt:

            print("\nSunucu kapatıldı.")

if __name__ == "__main__":

    start_server()

