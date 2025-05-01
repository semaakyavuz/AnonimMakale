import fitz  # PyMuPDF
import re
import spacy
import os

# NER modeli yükle
try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

def anonymize_pdf(input_path, output_path, keywords=[], secim=None):
    doc = fitz.open(input_path)

    if len(doc) > 0:
        page = doc[0]
        full_text = page.get_text()
        lines = full_text.splitlines()

        # ABSTRACT veya ÖZET satırının indexini bul
        abstract_index = next(
            (i for i, line in enumerate(lines) if "ABSTRACT" in line.upper() or "ÖZET" in line.upper()),
            None
        )

        # Başlık satırlarını bul
        title_lines = []
        if abstract_index is not None:
            for i in range(abstract_index):
                if lines[i].strip() and lines[i].isupper():
                    title_lines.append(i)
                elif title_lines:
                    break

            anonymize_start = max(title_lines) + 1 if title_lines else 0
            anonymize_lines = lines[anonymize_start:abstract_index]
            text_to_scan = "\n".join(anonymize_lines)
        else:
            text_to_scan = ""

        # ✅ Kutucuk kontrolleri
        ad_soyad_enabled = secim.ad_soyad if secim else False
        email_enabled = secim.e_posta if secim else False
        kurum_enabled = secim.kurum if secim else False

        # ✅ E-posta sansürle
        if email_enabled:
            email_matches = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text_to_scan)
            for email in email_matches:
                for inst in page.search_for(email.strip(".,;:()* ")):
                    page.add_redact_annot(inst, fill=(0, 0, 0))

        # ✅ Kurum adı kısmını parça bazlı sansürle
        if kurum_enabled:
            kurum_keywords = [
                "university", "institute", "faculty", "school", "department", "college",
                "research center", "government", "ministry", "council", "academy",
                "commission", "foundation", "organization", "agency", "education"
            ]

            for line in lines:
                line_lower = line.lower()
                for keyword in kurum_keywords:
                    if keyword in line_lower:
                        index = line_lower.find(keyword)
                        kurum_adayi = line[index:].strip(".,;:()* \n")
                        if len(kurum_adayi.split()) >= 2:
                            for inst in page.search_for(kurum_adayi):
                                page.add_redact_annot(inst, fill=(0, 0, 0))
                        break  # aynı satırda başka kurum arama, geç

        # ✅ Ad-soyad sansürle (manuel ve NER)
        if ad_soyad_enabled:
            temiz_keywords = [w for w in keywords if w and '@' not in w]

            for word in temiz_keywords:
                pattern = re.compile(re.escape(word), flags=re.IGNORECASE)
                for match in pattern.finditer(text_to_scan):
                    hit = match.group()
                    hit_variants = [hit, hit + ",", hit + ".", hit + ";", hit.upper()]
                    for variant in hit_variants:
                        for inst in page.search_for(variant.strip(".,;:()* ")):
                            page.add_redact_annot(inst, fill=(0, 0, 0))

            if nlp:
                doc_spacy = nlp(text_to_scan)
                for ent in doc_spacy.ents:
                    if (
                        getattr(ent, "label_", None) == "PERSON"
                        and getattr(ent, "text", None)
                        and "@" not in ent.text
                        and len(ent.text.strip()) > 1
                    ):
                        for inst in page.search_for(ent.text.strip(".,;:()* ")):
                            page.add_redact_annot(inst, fill=(0, 0, 0))

        page.apply_redactions()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc.save(output_path)
    doc.close()

def append_text_to_pdf(input_path, output_path, text_to_append):
    """
    Adds text to the end of a PDF file as a new page with proper Turkish character support.
    """
    # Open the PDF
    doc = fitz.open(input_path)
    
    # Create a new page at the end
    page = doc.new_page(-1)
    
    # Create text writer for better Unicode support
    tw = fitz.TextWriter(page.rect)
    
    # Set font with Turkish character support
    font = fitz.Font("Times-Roman")  # Built-in font with better Unicode support
    
    # Add the text with proper encoding
    tw.append((50, 50), text_to_append, font=font, fontsize=12)
    
    # Write the text to the page
    tw.write_text(page)
    
    # Save the modified PDF
    doc.save(output_path)
    doc.close()
