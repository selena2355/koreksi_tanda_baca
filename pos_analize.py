"""
ANALISIS LENGKAP: Hasil POS Tagging Stanza
File: Tembak_aku_docx_pos.json
"""

import json

# Load hasil
with open('./uploads/Tembak_aku.docx.pos.json', 'r') as f:
    results = json.load(f)

# Flatten data
all_tokens = []
for sentence in results:
    for token_data in sentence:
        all_tokens.append(token_data)

print("="*80)
print("📊 ANALISIS HASIL POS TAGGING")
print("="*80)
print(f"\nTotal tokens: {len(all_tokens)}")

# =========================================
# CASE 1: Kata "baca" (Expected: 3 cases)
# =========================================

print("\n" + "="*80)
print("CASE 1: Kata 'baca' (Ambiguous NOUN/VERB)")
print("="*80)

baca_cases = []
for i, token in enumerate(all_tokens):
    if token['token'].lower() == 'baca':
        # Get context
        prev_2 = all_tokens[i-2]['token'] if i >= 2 else ""
        prev_1 = all_tokens[i-1]['token'] if i >= 1 else ""
        next_1 = all_tokens[i+1]['token'] if i+1 < len(all_tokens) else ""
        
        baca_cases.append({
            'token': token['token'],
            'pos': token['upos'],
            'context': f"{prev_2} {prev_1} _baca_ {next_1}",
            'prev': prev_1
        })

print(f"\nDitemukan: {len(baca_cases)} kemunculan kata 'baca'")

for i, case in enumerate(baca_cases, 1):
    # Determine expected POS
    if case['prev'].lower() in ['tanda', 'kesalahan']:
        expected = 'NOUN'  # Compound noun
        correct = case['pos'] == 'NOUN'
    elif case['prev'].lower() in ['suka', 'tidak']:
        expected = 'VERB'  # After auxiliary/negation
        correct = case['pos'] == 'VERB'
    else:
        expected = '???'
        correct = None
    
    status = "✅ CORRECT" if correct else "❌ WRONG" if correct is False else "❓ UNCLEAR"
    
    print(f"\n{i}. Context: {case['context']}")
    print(f"   POS: {case['pos']:10s} | Expected: {expected:10s} | {status}")

# Score
baca_correct = sum(1 for c in baca_cases if 
                   (c['prev'].lower() == 'tanda' and c['pos'] == 'NOUN') or
                   (c['prev'].lower() == 'suka' and c['pos'] == 'VERB'))
print(f"\nAccuracy: {baca_correct}/{len(baca_cases)} ({baca_correct/len(baca_cases)*100:.1f}%)")


# =========================================
# CASE 2: Kata "sakit" (Expected: 3 cases)
# =========================================

print("\n" + "="*80)
print("CASE 2: Kata 'sakit' (Ambiguous NOUN/ADJ)")
print("="*80)

sakit_cases = []
for i, token in enumerate(all_tokens):
    if token['token'].lower() == 'sakit':
        prev_2 = all_tokens[i-2]['token'] if i >= 2 else ""
        prev_1 = all_tokens[i-1]['token'] if i >= 1 else ""
        next_1 = all_tokens[i+1]['token'] if i+1 < len(all_tokens) else ""
        
        sakit_cases.append({
            'token': token['token'],
            'pos': token['upos'],
            'context': f"{prev_2} {prev_1} _sakit_ {next_1}",
            'prev': prev_1
        })

print(f"\nDitemukan: {len(sakit_cases)} kemunculan kata 'sakit'")

for i, case in enumerate(sakit_cases, 1):
    if case['prev'].lower() == 'rumah':
        expected = 'NOUN'  # Compound: rumah sakit
        correct = case['pos'] == 'NOUN'
    elif case['prev'].lower() in ['yang', 'kondisi']:
        expected = 'ADJ'  # Adjective describing state
        correct = case['pos'] == 'ADJ'
    else:
        expected = '???'
        correct = None
    
    status = "✅ CORRECT" if correct else "❌ WRONG" if correct is False else "❓ UNCLEAR"
    
    print(f"\n{i}. Context: {case['context']}")
    print(f"   POS: {case['pos']:10s} | Expected: {expected:10s} | {status}")

sakit_correct = sum(1 for c in sakit_cases if 
                    (c['prev'].lower() == 'rumah' and c['pos'] == 'NOUN') or
                    (c['prev'].lower() in ['yang', 'kondisi'] and c['pos'] == 'ADJ'))
print(f"\nAccuracy: {sakit_correct}/{len(sakit_cases)} ({sakit_correct/len(sakit_cases)*100:.1f}%)")


# =========================================
# CASE 3: Kata "baru" (Expected: 5 cases)
# =========================================

print("\n" + "="*80)
print("CASE 3: Kata 'baru' (Ambiguous ADJ/ADV)")
print("="*80)

baru_cases = []
for i, token in enumerate(all_tokens):
    if token['token'].lower() == 'baru':
        prev_2 = all_tokens[i-2]['token'] if i >= 2 else ""
        prev_1 = all_tokens[i-1]['token'] if i >= 1 else ""
        next_1 = all_tokens[i+1]['token'] if i+1 < len(all_tokens) else ""
        
        baru_cases.append({
            'token': token['token'],
            'pos': token['upos'],
            'context': f"{prev_2} {prev_1} _baru_ {next_1}",
            'prev': prev_1,
            'next': next_1
        })

print(f"\nDitemukan: {len(baru_cases)} kemunculan kata 'baru'")

for i, case in enumerate(baru_cases, 1):
    # ADJ: "Teknologi baru", "Penelitian baru"
    # ADV: "baru saja", "baru dikembangkan", "yang baru"
    
    if case['prev'].lower() in ['teknologi', 'penelitian']:
        expected = 'ADJ'  # Modifying noun (new X)
        correct = case['pos'] == 'ADJ'
    elif case['next'].lower() in ['saja', 'dikembangkan', 'diluncurkan']:
        expected = 'ADV'  # Temporal adverb (just/recently)
        correct = case['pos'] == 'ADV'
    elif case['prev'].lower() == 'yang':
        expected = 'ADV'  # "yang baru" = recently
        correct = case['pos'] == 'ADV'
    else:
        expected = '???'
        correct = None
    
    status = "✅ CORRECT" if correct else "❌ WRONG" if correct is False else "❓ UNCLEAR"
    
    print(f"\n{i}. Context: {case['context']}")
    print(f"   POS: {case['pos']:10s} | Expected: {expected:10s} | {status}")

baru_correct = sum(1 for c in baru_cases if 
                   (c['prev'].lower() in ['teknologi', 'penelitian'] and c['pos'] == 'ADJ') or
                   (c['next'].lower() in ['saja', 'dikembangkan', 'diluncurkan'] and c['pos'] == 'ADV') or
                   (c['prev'].lower() == 'yang' and c['pos'] == 'ADV'))
print(f"\nAccuracy: {baru_correct}/{len(baru_cases)} ({baru_correct/len(baru_cases)*100:.1f}%)")


# =========================================
# CASE 4: Kata "lama" (Expected: 4 cases)
# =========================================

print("\n" + "="*80)
print("CASE 4: Kata 'lama' (Ambiguous ADJ/ADV)")
print("="*80)

lama_cases = []
for i, token in enumerate(all_tokens):
    if token['token'].lower() == 'lama':
        prev_2 = all_tokens[i-2]['token'] if i >= 2 else ""
        prev_1 = all_tokens[i-1]['token'] if i >= 1 else ""
        next_1 = all_tokens[i+1]['token'] if i+1 < len(all_tokens) else ""
        
        lama_cases.append({
            'token': token['token'],
            'pos': token['upos'],
            'context': f"{prev_2} {prev_1} _lama_ {next_1}",
            'prev': prev_1
        })

print(f"\nDitemukan: {len(lama_cases)} kemunculan kata 'lama'")

for i, case in enumerate(lama_cases, 1):
    # ADV: "berlangsung lama", "Sudah lama"
    # ADJ: "yang lama", "cukup lama"
    
    if case['prev'].lower() in ['berlangsung', 'sudah']:
        expected = 'ADV'  # Temporal adverb
        correct = case['pos'] == 'ADV'
    elif case['prev'].lower() in ['yang', 'cukup']:
        expected = 'ADJ'  # Adjective describing duration
        correct = case['pos'] == 'ADJ'
    else:
        expected = '???'
        correct = None
    
    status = "✅ CORRECT" if correct else "❌ WRONG" if correct is False else "❓ UNCLEAR"
    
    print(f"\n{i}. Context: {case['context']}")
    print(f"   POS: {case['pos']:10s} | Expected: {expected:10s} | {status}")

lama_correct = sum(1 for c in lama_cases if 
                   (c['prev'].lower() in ['berlangsung', 'sudah'] and c['pos'] == 'ADV') or
                   (c['prev'].lower() in ['yang', 'cukup'] and c['pos'] == 'ADJ'))
print(f"\nAccuracy: {lama_correct}/{len(lama_cases)} ({lama_correct/len(lama_cases)*100:.1f}%)")


# =========================================
# CASE 5: Kata "baik" (Expected: 1 case)
# =========================================

print("\n" + "="*80)
print("CASE 5: Kata 'baik' (Ambiguous ADJ/ADV)")
print("="*80)

baik_cases = []
for i, token in enumerate(all_tokens):
    if token['token'].lower() == 'baik':
        prev_2 = all_tokens[i-2]['token'] if i >= 2 else ""
        prev_1 = all_tokens[i-1]['token'] if i >= 1 else ""
        next_1 = all_tokens[i+1]['token'] if i+1 < len(all_tokens) else ""
        
        baik_cases.append({
            'token': token['token'],
            'pos': token['upos'],
            'context': f"{prev_2} {prev_1} _baik_ {next_1}",
            'prev': prev_1
        })

print(f"\nDitemukan: {len(baik_cases)} kemunculan kata 'baik'")

for i, case in enumerate(baik_cases, 1):
    # Expected: "dengan baik" = ADV
    if case['prev'].lower() in ['dengan', 'sangat']:
        expected = 'ADV'
        correct = case['pos'] == 'ADV'
    else:
        expected = 'ADJ'
        correct = case['pos'] == 'ADJ'
    
    status = "✅ CORRECT" if correct else "❌ WRONG" if correct is False else "❓ UNCLEAR"
    
    print(f"\n{i}. Context: {case['context']}")
    print(f"   POS: {case['pos']:10s} | Expected: {expected:10s} | {status}")


# =========================================
# CASE 6: Abbreviations
# =========================================

print("\n" + "="*80)
print("CASE 6: Abbreviations (dkk, dll, gelar akademik)")
print("="*80)

abbrev_tokens = ['dkk', 'dll', 'S', 'M', 'T', 'Dr', 'Kom']
abbrev_cases = []

for i, token in enumerate(all_tokens):
    if token['token'] in abbrev_tokens:
        # Check if part of academic degree (preceded by punctuation)
        prev_1 = all_tokens[i-1]['token'] if i >= 1 else ""
        next_1 = all_tokens[i+1]['token'] if i+1 < len(all_tokens) else ""
        
        # Build full abbreviation context
        if token['token'] in ['S', 'M', 'Dr'] and next_1 == '.':
            # Might be part of S.Kom., M.Kom., Dr.
            context_tokens = []
            j = i
            while j < len(all_tokens) and j < i + 10:
                context_tokens.append(all_tokens[j]['token'])
                if all_tokens[j]['token'] == '.' and j > i:
                    # Check if next is comma or end
                    if j+1 >= len(all_tokens) or all_tokens[j+1]['token'] in [',', '.', 'dari', 'dan']:
                        break
                j += 1
            
            full_abbrev = ''.join(context_tokens)
            
            abbrev_cases.append({
                'token': token['token'],
                'full': full_abbrev,
                'pos': token['upos'],
                'context': f"... {prev_1} _{token['token']}_ {next_1} ..."
            })

print(f"\nDitemukan: {len(abbrev_cases)} abbreviation tokens")

# Also find standalone dkk, dll
for i, token in enumerate(all_tokens):
    if token['token'].lower() in ['dkk', 'dll']:
        prev_1 = all_tokens[i-1]['token'] if i >= 1 else ""
        next_1 = all_tokens[i+1]['token'] if i+1 < len(all_tokens) else ""
        
        abbrev_cases.append({
            'token': token['token'],
            'full': token['token'] + '.',
            'pos': token['upos'],
            'context': f"... {prev_1} _{token['token']}_ {next_1} ..."
        })

print(f"Total dengan dkk/dll: {len(abbrev_cases)} cases\n")

# Analyze
for i, case in enumerate(abbrev_cases[:10], 1):  # Show first 10
    # Abbreviations typically tagged as X or PROPN
    expected = 'X or PROPN'
    status = "✅ OK" if case['pos'] in ['X', 'PROPN', 'NOUN'] else "❌ UNEXPECTED"
    
    print(f"{i}. {case['full']:15s} → POS: {case['pos']:10s} | Expected: {expected} | {status}")

print("\n📝 Note: Abbreviations inconsistent - X, PROPN, or NOUN")


# =========================================
# CASE 7: Compound Nouns
# =========================================

print("\n" + "="*80)
print("CASE 7: Compound Nouns (tanda baca, rumah sakit, hak cipta)")
print("="*80)

compounds = [
    ('tanda', 'baca'),
    ('rumah', 'sakit'),
    ('hak', 'cipta')
]

compound_cases = []

for i, token in enumerate(all_tokens[:-1]):
    next_token = all_tokens[i+1]
    
    # Check if forms known compound
    pair = (token['token'].lower(), next_token['token'].lower())
    
    if pair in compounds:
        compound_cases.append({
            'word1': token['token'],
            'pos1': token['upos'],
            'word2': next_token['token'],
            'pos2': next_token['upos'],
            'compound': f"{token['token']} {next_token['token']}"
        })

print(f"\nDitemukan: {len(compound_cases)} compound noun cases\n")

for i, case in enumerate(compound_cases, 1):
    # Expected: Both should be NOUN
    correct = case['pos1'] == 'NOUN' and case['pos2'] == 'NOUN'
    status = "✅ CORRECT" if correct else "❌ WRONG"
    
    print(f"{i}. Compound: {case['compound']}")
    print(f"   {case['word1']:10s} → {case['pos1']:10s}")
    print(f"   {case['word2']:10s} → {case['pos2']:10s}")
    print(f"   Expected: NOUN + NOUN | {status}\n")


# =========================================
# CASE 8: Foreign/Technical Terms
# =========================================

print("\n" + "="*80)
print("CASE 8: Foreign/Technical Terms")
print("="*80)

foreign_terms = ['preprocessing', 'tokenisasi', 'online', 'machine', 'learning', 
                 'deep', 'pos', 'tagging', 'NLP', 'ML', 'AI']

foreign_cases = []

for i, token in enumerate(all_tokens):
    if token['token'].lower() in [t.lower() for t in foreign_terms]:
        prev_1 = all_tokens[i-1]['token'] if i >= 1 else ""
        next_1 = all_tokens[i+1]['token'] if i+1 < len(all_tokens) else ""
        
        foreign_cases.append({
            'token': token['token'],
            'pos': token['upos'],
            'context': f"... {prev_1} _{token['token']}_ {next_1} ..."
        })

print(f"\nDitemukan: {len(foreign_cases)} foreign/technical term cases\n")

for i, case in enumerate(foreign_cases[:15], 1):  # Show first 15
    # Expected: mostly X (unknown) or NOUN/PROPN
    expected = "X, NOUN, or PROPN"
    status = "✅ OK" if case['pos'] in ['X', 'NOUN', 'PROPN'] else "⚠️ UNEXPECTED"
    
    print(f"{i}. {case['token']:15s} → POS: {case['pos']:10s} | {status}")

print("\n📝 Note: Foreign terms often tagged as X (unknown)")


# =========================================
# OVERALL SUMMARY
# =========================================

print("\n" + "="*80)
print("📊 OVERALL SUMMARY")
print("="*80)

total_target = len(baca_cases) + len(sakit_cases) + len(baru_cases) + len(lama_cases) + len(baik_cases)
total_correct = baca_correct + sakit_correct + baru_correct + lama_correct

print(f"\n🎯 Ambiguous Words (baca, sakit, baru, lama, baik):")
print(f"   Total cases: {total_target}")
print(f"   Correct: {total_correct}")
print(f"   Wrong: {total_target - total_correct}")
print(f"   Accuracy: {total_correct/total_target*100:.1f}%")

print(f"\n📝 Breakdown:")
print(f"   baca  : {baca_correct}/{len(baca_cases)} ({baca_correct/len(baca_cases)*100:.1f}%)")
print(f"   sakit : {sakit_correct}/{len(sakit_cases)} ({sakit_correct/len(sakit_cases)*100 if len(sakit_cases) > 0 else 0:.1f}%)")
print(f"   baru  : {baru_correct}/{len(baru_cases)} ({baru_correct/len(baru_cases)*100 if len(baru_cases) > 0 else 0:.1f}%)")
print(f"   lama  : {lama_correct}/{len(lama_cases)} ({lama_correct/len(lama_cases)*100 if len(lama_cases) > 0 else 0:.1f}%)")
print(f"   baik  : {len(baik_cases)} case(s)")

print(f"\n💡 Observations:")
print(f"   - Compound nouns: {len(compound_cases)} cases found")
print(f"   - Abbreviations: {len(abbrev_cases)} cases (inconsistent: X/PROPN/NOUN)")
print(f"   - Foreign terms: {len(foreign_cases)} cases (mostly X)")

print("\n" + "="*80)
print("✅ ANALYSIS COMPLETE")
print("="*80)