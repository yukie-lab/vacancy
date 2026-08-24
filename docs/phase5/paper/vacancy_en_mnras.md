<!-- MNRAS 版: scripts/build_mnras_version.py で md 版から機械生成(裁定 #7)。本文・数値は md 版と同一。 -->
# A Vacancy Atlas of the Solar Neighbourhood: Star-by-Star, Technology-Band-Conditional Upper Bounds on Occupation from Heterogeneous Non-Detections

**Yukie Maeda**
Independent Researcher, Tokyo
ORCID: 0009-0005-3401-9230
(Preprint, English version; a Japanese version accompanies this record; doi:10.5281/zenodo.22081202)
Footnote: The roles of AI systems and the complete verification protocol are disclosed in Appendix B; this internal verification is not a substitute for human peer review.


## Abstract

For each star in the solar neighbourhood we aggregate conditional non-detections ("facilities of band T at this star would have been detected by survey set S") into a star-by-star, band-conditional upper bound on occupation, P(occupied | D, T, π), as a function of the prior π. To our knowledge no star-level ledger of this quantity exists. The population is 332,571 stars within 100 pc (Gaia EDR3 GCNS basis)[^pop]. The claimed bands are three radio bands (T-R1: EIRP ≥ 10¹³ W; T-R2: ≥ 10¹⁷ W; T-R3: Earth-level radar-type intermittent leakage) within [1.10, 3.45] GHz. Detection probabilities are imported from the 356,616 observation rows of Wlodarczyk-Sroka et al. (2020); observations within one modality are merged by marginalising shared latent variables, and we prove that the naive likelihood product tilts toward "vacancy". Thresholds and pass criteria were pre-registered before aggregation (doi:10.5281/zenodo.22067884). Verification: G1 monotonicity, 6,777 checks, 0 violations; G2 independent implementations agree to 4.9 × 10⁻¹⁰ dex; G3: the WS20 1/N limit is reproduced exactly at ≤50 pc (N = 1513), the Hephaistos I count fails (the waste-heat band is demoted), and the Solar-System self-test passes. Stars with a bound number 1,554 (T-R1), 1,587 (T-R2) and 159 (T-R3); 330,984 stars (99.52%) are undecidable — a main result. In T-R3 posterior ≈ prior (Λ ≥ 0.998): the lowest band the atlas can speak about is calibrated by Earth itself. Joined with reachability and settlement resources, 815 stars are flyby-reachable with a T-R1 bound. At the Gaia DR4 release (2026-12-02) only the distance-dependent part of the ledger is recomputed (v1.1). These bounds are survey quantities, not proofs of absence, and license no inference about settlement (§7.1).

[^pop]: Source: `data/phase1/ledger_v0_summary.json` (population). Throughout, the provenance of each number is given in footnotes or table notes; nothing is recomputed in this paper.

## 1. Introduction

### 1.1 The core question
Searches for extraterrestrial technology over 60 years have accumulated non-detections, but a non-detection is not the proposition "nobody is anywhere"; it is a star-level, conditional fact: "when this survey looked at this star, at this sensitivity, in this band, at this time, there was no trace". Our question is what the **star-by-star, band-conditional upper bound on occupation** looks like once those conditional non-detections are aggregated heterogeneously per star. This quantity differs from population-model limits (the Grimaldi family) and from the coverage fraction of search-parameter volume (the Wright et al. 2018 haystack), and to our knowledge it has not previously been tabulated.

### 1.2 Motivation
The motivation is twofold. First, to provide a basic survey for thinking about the expansion of the human habitat as "looking for places that are vacant" rather than as invasion. Second, to contribute a star-level evidence ledger to the puzzle of the rarity of technology in the universe. We elevate the ethical requirement into methodology: every statement is written as a probability statement carrying the conditional clause "with respect to facilities of band T, under survey set S", and no absolute "vacant" is ever asserted (§7.1).

### 1.3 Contributions
(i) A star-by-star, band-resolved ε and Λ ledger for 332,571 stars with provenance. (ii) A merging rule that marginalises shared latent variables within a modality, and a theorem that the naive product tilts toward vacancy (§3.4). (iii) Two-stage pre-registration (factor structure → thresholds and pass criteria) with public deviation records. (iv) The discipline of reading the undecidable accounting as a main result. (v) Cross-tabulation with reachability and settlement resources without composition.

### 1.4 Outline
§2 position; §3 method; §4 verification including the deviation section; §5 results; §6 the three-axis atlas; §7 discussion (7.1 interpretation and scope; 7.2 limitations and outlook); Appendices A–D.

## 2. Position

**Relative to the Grimaldi family (probabilistic population models)**: Grimaldi (2017) and related work derive expected detection rates from probabilistic models of transmitter distribution and lifetime. We tabulate the likelihood ratio Λ_i(T) per star i and make no population assumption (π is swept).
**Relative to the Wright et al. (2018) haystack**: that work discusses the fractional coverage of the search-parameter volume. We project it onto individual stars and count the holes in coverage per star as "undecidable"; the 99.52% undecidable fraction (§5.2) is the star-level version of haystack incompleteness.
**Relative to Breakthrough Listen and Ĝ/Hephaistos**: Price et al. (2020) and Wlodarczyk-Sroka et al. (2020; hereafter WS20) report new radio observations and population limits; Wright et al. (2014), Griffith et al. (2015), and Suazo et al. (2022, 2024) search for mid-infrared waste heat. We perform no new observation and **aggregate these existing non-detections heterogeneously per star**. The Phase 0 survey established that Ĝ provides no per-star limits for nearby stars (it targets galaxies) and that Hephaistos closes methodologically in the published literature but releases no per-star table[^p0].
**Diversity of limit formulae**: the percentage limits of Price et al. (2020) §5.3 (formula not stated), the 1/N of WS20, our exact binomial limit, and our star-level Bayesian bound are all **different quantities** (§4.3, §7.1).

[^p0]: `docs/phase0/01-machine-readability-survey.md`.

## 3. Method

### 3.1 Population and stellar basis
GCNS (Gaia Collaboration, Smart et al. 2021; VizieR J/A+A/649/A6): 331,312 stars within 100 pc, plus the catalogue's `missing` table of 1,259 bright stars without an EDR3 solution: 332,571 stars[^pop]. EDR3 source_ids are identical to DR3. Distances are GCNS dist_50. WS20 stars (Gaia DR2 ids) were matched to EDR3 by position and proper motion (1,534/1,671 = 91.8% at ≤100 pc; the remainder are mostly bright stars without EDR3 solutions, of which 67 observation rows for 42 stars were recovered through the `missing` table — the Phase 0 survey value of 43 counts DR2 entries, two of which correspond to HD 239960A)[^gc].

[^gc]: `data/phase0/gcns_stats.json`; `data/phase1/ledger_v0_summary.json` (n_rows_matched_missing_table).

### 3.2 Declared technology bands
A technology band T is a member of a declared finite set of classes (Constitution Art. 3.1).
- **T-R1**: narrowband (δν = 1 Hz), continuous transmission, EIRP ≥ 10¹³ W (Arecibo planetary-radar class). The transmission frequency ν is declared uniform within the window [1.10, 3.45] GHz (gaps inside the window are expressed on the ε(ν) side).
- **T-R2**: as above with EIRP ≥ 10¹⁷ W.
- **T-R3**: Earth-level radar-type intermittent leakage, EIRP_peak = 10¹¹ W (evaluated at the top of the class), illumination factor f_ill = f_duty·f_beam ∈ [10⁻⁵, 10⁻²] (log-uniform; marginalised as a per-star latent variable). Broadcast-type leakage (~10⁶ W) lies below the band.
- **T-W1 (information layer)**: partial-Dyson-sphere waste heat (γ ≥ 0.1, T_DS ∈ [100, 700] K). Because the G3(ii) anchor failed, v1 makes no vacancy claim in this band (§4.4, §5.5).
- The extension shelf (optical lasers, transients, unpublished C/X-band and UWL observations) is undecidable.

### 3.3 Factor structure of the detection probability ε
For observation s (telescope × receiver × pointing), star i, and band T: ε_{s,i}(T; ν) = Θ_sens · 1[ν ∈ B_s] · f_pipe · f_duty · f_drift · f_beam.
- Sensitivity: Θ_sens = 1[EIRP_min,s,i ≤ EIRP_T], EIRP_min = EIRP50 (d/50 pc)² / R(θ), EIRP50 = 2.1 × 10¹² W (GBT L/S) and 9.1 × 10¹² W (Parkes 10-cm) (Price et al. 2020 §5.2), R(θ) = exp(−4 ln 2 (θ/FWHM)²) (WS20 §3). Recomputing all 356,616 WS20 rows with this formula gives a median ratio of 1.0000[^ws]. The class is evaluated at its weakest member (exactly at threshold), i.e. conservatively.
- Band coverage: B_s is the receiver band minus notches (GBT L 0.66 GHz, GBT S 0.94 GHz, Parkes 10-cm 0.85 GHz; union 2.15 GHz of the 2.35 GHz window).
- f_pipe = 0.5 (per-observation detection probability of Price et al. 2020 §5.3, including RFI obscuration). f_duty = f_drift = f_beam = 1 by class declaration for T-R1/R2.
- T-W1: the Hephaistos model (grey absorption (1−γ), blackbody re-emission) predicts the colour excess in G−W3 / G−W4; detection is an excess of k = 3 σ from the main-sequence locus. Stars already in excess are "detection candidates" and undecidable.

[^ws]: `data/phase0/ws20_stats.json` (eirp_recalc_check).

### 3.4 Merging rule (latent-variable marginalisation) and theorem
Observations within one modality are merged into a single ε by marginalising the shared latent variable (radio: ν; intermittent band: f_ill; waste heat: T_DS), and products are taken only across modalities:

  1 − ε^rad_i(T) = Σ_c w_c Π_{s∈rad(i)} [1 − ε_{s,i}(T)·1[c ⊂ B_s]],  T-R3: 1 − ε^rad_i = Σ_f w_f Σ_c w_c Π_s [1 − Θ_s f_pipe f·1[c ⊂ B_s]]

where c runs over the 9 intervals into which the window is cut by receiver-band and notch boundaries (one grid shared by the whole modality), w_c are width fractions, and f runs over a 13-point log grid.

**Theorem (vacancy-ward bias of the naive product).** **Premises**: (a) the transmission frequency ν is a single unknown shared by all observations, with a uniform prior on the window; (b) observations in the same receiver band share the coverage interval B, with an in-band detection probability p equal for each observation and zero out of band; (c) observations are conditionally independent given ν. Then for two observations in the same band the exact non-detection probability (= Λ) is 1 − c(1 − (1−p)²) = 1 − c(2p − p²) with c = |B|/|window|, the naive product is (1 − cp)², and **(1 − cp)² < 1 − c(2p − p²)** for 0 < c < 1 and 0 < p ≤ 1. For p = 1 the exact value is 1 − c while the naive product is (1−c)². **Proof**: [1 − c(2p − p²)] − (1−cp)² = c p² (1 − c) > 0. ∎ The naive product under-estimates the non-detection probability Λ (over-estimates detection), lowers the posterior occupation expit(logit π + ln Λ), and thus tilts toward "vacancy". The unit test `test_merge_rule_same_band_twice` pins this inequality. Likewise, drawing f_ill independently per observation row contradicts the fact that f_beam (transmitter-side geometry) is fixed with respect to the observer and produces an error in the same direction. Full sharing of f_ill is a conservative declaration: the true structure lies between shared f_beam and partially independent f_duty, and by Jensen's inequality full sharing places ε on the lower side, i.e. it under-reports detection power and tilts toward being unable to exclude occupation.

### 3.5 Aggregation and the π sweep
Λ_i(T) = 1 − ε^m_i(T) (in v1 each band is a single modality). P(occupied | D, T, π) = expit(logit π + ln Λ_i(T)). π is swept over 51 logarithmic points in [10⁻⁶, 0.5]; representative values π = 10⁻³, 10⁻², 10⁻¹ are tabulated. No single number is called "the vacancy". All arithmetic is done in log space (logsumexp).

### 3.6 Two-stage pre-registration
(a) End of Phase 0: the band set, the factor structure of ε, and the merging rule were fixed at commit `10a01e71…` (Appendix D; private). (b) End of Phase 1: thresholds, the aggregation formula, the G1–G3 pass criteria, and the Monte-Carlo declaration were registered publicly on Zenodo (doi:10.5281/zenodo.22067884, sha256 88eb7809…), and only then was the aggregation run. Any later change is a deviation and is recorded in §4.6.

### 3.7 Independence assumptions
Assumptions remaining after merging are declared: independence of f_pipe across observations (the same premise as Price et al. 2020; sensitivity range U[0.3, 0.8]); temporal independence of duty cycle (T-R1/R2 are continuous-transmission classes); per-star sharing of the T-R3 illumination factor; per-star sharing of distance; OR-merging of the W3/W4 decisions; an empirical main-sequence locus; and a monochromatic approximation of the Dyson-sphere blackbody flux (±10%).

### 3.8 Data provenance
The WS20 table (VizieR J/MNRAS/498/5720, 356,616 rows)[^ws]; the Breakthrough Listen open data archive (per-target observation files: 6,219 HIP targets, 100% with observation date and centre frequency, 95,529 files; 1,934 of the 2,259 radio observation rows carry an MJD)[^bl]; GCNS; HGCA (Hipparcos–Gaia cross-match, 6,219 BL targets → 5,963 DR3 ids); the Mamajek table (M_G → log L, colour → type); the NASA Exoplanet Archive (pscomppars, retrieved 2026-08-23); and the HWC (retrieved 2026-08-23). SHA-256 checksums of all inputs are in Appendix D.

[^bl]: `data/phase0/bl_log_stats.json`; `data/phase1/ledger_v0_summary.json` (rows_with_bl_dates).

## 4. Verification

### 4.1 G1 — monotonicity and Monte-Carlo stability
Adding observation rows one at a time, the sequence of Λ must be non-increasing; this was checked for all 1,587 stars × 3 bands: **6,777 checks, 0 violations** (tolerance +10⁻¹²)[^g1]. In the Monte Carlo (N = 1,000, seed = 20260823, sharing units as pre-registered in §4 of the frozen document) the median 90% width of log₁₀Λ in the radio bands is 0.094 dex (dominated by the f_pipe perturbation and proportional to the number of rows); low-confidence cells (width > 0.5 dex) number 0 in the three radio bands. In the W1 information layer there are 25,822 low-confidence cells (γ = 0.1), but 97% of them arise from a discrete jump between Λ = 0 (clipped) and a small positive value; seen at the posterior for π = 10⁻², the conclusion "occupation probability ≲ 10⁻³" is unchanged.

[^g1]: `data/phase2/g1_report.json`.

### 4.2 G2 — two independent implementations
An export without any Λ column (the per-star, per-band, per-interval ε rows and interval weights) was handed to the staff officer (chat Claude) before aggregation, who recomputed Λ independently by log-sums. The comparison gave max|Δlog₁₀Λ| = 4.9 × 10⁻¹⁰ (radio) and 5.2 × 10⁻⁷ (waste heat), tolerance 10⁻⁶, 0 violations[^g2].

[^g2]: Ruling log, "G2 pass".

### 4.3 G3(i) — WS20 / Price anchors
(a) **Report (no pass/fail)**: against the published 0.45% / 0.37% / 2.0% of Price et al. (2020) §5.3 (GBT L / GBT S / Parkes; N = 882 / 1005 / 189), our exact binomial 95% limits f = [1 − 0.05^{1/N}] / 0.5 are 0.678% / 0.595% / 3.15% (ratios 1.51 / 1.61 / 1.57). The original formula is not stated in the source; the products f·N implied by the three published values, 3.97 / 3.72 / 3.78, scatter and cannot be reproduced simultaneously by any single standard formula[^g3].
(b) **Hard gate**: we recounted using only the WS20 `rest` distances (DR2 basis; EDR3 distances not used). The published "EIRP ≳ 6.5 × 10¹³ / 2.5 × 10¹⁴ W" are the maxima of EIRP_min inside the shells (recount 6.49 × 10¹³ / 2.49 × 10¹⁴ W), not selection cuts. ≤50 pc: **N = 1513 (exact match)**, 1/N = 0.0661% (published ≲0.0660%); ≤100 pc: N = 1671, 0.0598% (published 0.061 +0.001/−0.003 %); ≤200 pc: N = 2576, 0.0388% (published 0.039 +0.004/−0.008 %). The ≤100/200 pc values lie inside the published error intervals (the pass criterion follows the deviation of §4.6).
(c) **A different quantity**: in the same shells the mean of our star-level posterior is 7.7 × 10⁻⁴ / 7.7 × 10⁻³ at π = 10⁻³ / 10⁻² (mean Λ ≈ 0.767; ≤50 pc, 1,436 stars with status ok). 1/N is a frequentist limit from "N non-detection trials" that contains neither coverage nor sensitivity factors, whereas our posterior mean is a function of π; their coincidence in order of magnitude at π = 10⁻³ follows from Λ ≈ 0.77 being close to 1 and is not an agreement.

[^g3]: `data/phase3/g3_report.json`.

### 4.4 G3(ii) — Hephaistos I count reproduction (fail)
We counted the "fraction compatible with (unable to exclude) a Dyson sphere" of Suazo et al. (2022) Table 1 (100 pc, N = 265,724, T_DS = 300 K): 6.6 × 10⁻³ / 1.9 × 10⁻⁴ / 1.8 × 10⁻⁵ for γ = 0.1 / 0.5 / 0.9, with our population (GCNS ≤100 pc 300,567 → main sequence 276,814 → with WISE photometry 187,274) and our excess test. With "compatible" = "θ₃ = θ₄ = 0 in the 300 K interval" or "already a detection candidate" (definition A), the compatible fractions are 2.07 × 10⁻² / 1.77 × 10⁻² / 1.77 × 10⁻², ratios **3.13 / 93 / 982**, outside the frozen criterion (ratio 0.3–3): **fail**[^g3].
**Directional analysis (not a computational error)**: the explosion of the ratio with γ arises because our "detection candidates" (≥3σ excess, 3,304 stars) are placed, by Art. 5.3, on the "cannot exclude" side **for every γ**. The Hephaistos "inside the DS region" is membership in the model region for a given (γ, T), and a mild 0.2 mag excess is inconsistent with γ = 0.9 (several magnitudes). Ours is the consequence of a conservative design that claims fewer exclusions than Hephaistos, not a computational error (G1 and G2 pass for W1 as well).
**Diagnostic with definition B** (not adopted): taking as compatible the stars whose observed residual agrees with the (γ, 300 K) model residual within kσ_tot, the ratios are 0.82 at γ = 0.1, 0.17 at γ = 0.5 (6 stars versus ~36 expected; not explicable by Poisson fluctuations; unresolved), and 0.30 at γ = 0.9 (~1 versus ~3.4 stars; small-number statistics; undecidable). Because this would be a post-hoc choice of the compatibility definition after seeing the numbers, it is not adopted, and no word suggesting a pass is used.
**Consequence**: by Art. 6 (a band derived in this work requires a passed G3 anchor as a precondition for publication) T-W1 was demoted to the extension shelf (information layer, claim=false).
**Promotion path**: re-adjudication if a per-star Hephaistos-type table is published, or if an independent anchor can be built at the DR4 merge (v1.1). We do not request such data.

### 4.5 G3(iii) — Solar-System self-test (pass)
The Solar System was passed through T-R3 as virtual rows at 24 distances d = 1.3–10.8 pc (GBT L + GBT S + Parkes 10-cm, on axis, one row each, EIRP_peak = 10¹¹ W). At every d, Λ(marginalised) ≥ 0.999085 and Λ(f_ill at its upper end 10⁻²) ≥ 0.99479 — **posterior ≈ prior**, pass[^g3]. Red-flag check: in the extreme f_ill = f_pipe = 1, Λ = 1 − 2.15/2.35 = 0.0851 < 0.5 (for d ≤ 4.8 pc all three bands are sensitive), i.e. Earth "would be detected". The detector ε is alive; posterior ≈ prior in T-R3 results from the smallness of the illumination factor (intermittency and beaming). Parkes 10-cm loses sensitivity beyond d = 5.24 pc; GBT keeps it to 10.9 pc (Figure 1).

[FIG] figs/fig1_g3iii_dlambda.png | Figure 1: the G3(iii) Solar-System self-test as d–Λ. Three curves (marginalised; f_ill = 10⁻², the upper end; the extreme f_ill = f_pipe = 1) with the sensitivity boundaries (Parkes 5.24 pc, GBT 10.9 pc). Values are the frozen g3_iii.json. Reproduce: python3 scripts/build_paper_figs.py


### 4.6 Deviation section (Art. 9.3) — two cases in which the institution worked
**Ruling #3 (deviation: revision of a criterion)**. The frozen document §5 set the G3(i)(b) pass criterion for the ≤100/200 pc shells at "published central value ±1%". The recount 0.0598% was −1.89% from the published 0.061% — **fail** — and work stopped. The staff officer's consultation of the source showed that WS20 §3 quotes the 50 pc shell increment as +42/−7 alongside the count under the EIRP ≥ 10¹³ W condition as 1513 (+9/−7), and that our `b_rest` recount (+42) matches the source's +42 exactly: the recount machinery behaves identically to the source, the central-value counting procedure is not uniquely recoverable from the text, and the substance of the failure was **a criterion designed without checking the published error bars at freezing time**. The criterion was revised to "inside the published explicit error interval" (the exact-match requirement at ≤50 pc and the recount procedure unchanged), and the new criterion passes. The fact of failure under the old criterion is kept on record. Error ledger E-1 (inadequate pre-freeze inspection by the staff officer) and E-2 (the sequence of events).
**Ruling #4 (not a deviation: acceptance of a failure under the criterion)**. G3(ii) failed under the frozen criterion; replacing the verdict through a post-hoc compatibility definition (definition B) was not adopted, and T-W1 was demoted. Acceptance of a failure without changing the criterion is the counterpart of the criterion revision (Ruling #3).
Self-reported items: one omission of an approved addendum sentence at the re-submission of revision 2; a subtraction error in the BL download tally script (no download was missed); a shell-expansion loss in a ruling-log path string; quoting the rounded four-digit lower bound of Λ in T-R3 with an inequality sign (E-7; corrected, with the exact minimum 0.998458 given alongside); and conflating the complement label of a cross count (E-8; correctly, 13,984 without a bound = 13,982 undecidable + 2 observed-but-insensitive). None affects any numerical conclusion (Appendix B).

## 5. Results

### 5.1 Overview of the ledger
Stars carrying a vacancy bound (ε determined) number **1,554** in T-R1, **1,587** in T-R2, and **159** in T-R3 (d ≤ 10.8 pc)[^s1]. Stars observed but insensitive in the band (ε = 0, Λ = 1 = no information) number 33 in T-R1 and 1,428 in T-R3. In T-R1, Λ ranges from 0.4266 (minimum: four rows, GBT L + GBT S + GBT S + Parkes 10-cm, i.e. two S-band pointings, one star) through 0.8000 (median: GBT S only) to 0.8596 (maximum: GBT L only), with a median posterior of 0.0080 at π = 10⁻². In T-R3, Λ = 0.9985–0.9998 (rounded to four digits; exact minimum 0.998458) and the posterior at π = 10⁻² is 0.0100. Λ is set by the coverage structure of the observation rows (in-window coverage of the receiver × f_pipe) and hardly by distance (only 33 stars straddle the sensitivity threshold in T-R1; Figure 2).

[FIG] figs/fig2_coverage_lambda.png | Figure 2: receiver coverage of the declared window [1.10, 3.45] GHz (top: the 9 common intervals and notches) and the merged Λ for the six most frequent observation-row combinations present in the ledger (bottom: T-R1; 1,515 stars in total, the remaining 39 stars being rarer combinations of three or more rows; bar colours follow the posterior colour rule at π = 10⁻²). Values are the frozen radio_obs_v0.json and lambda_ledger.json. Reproduce: python3 scripts/build_paper_figs.py


[^s1]: `data/phase2/lambda_ledger.json` (summary.status_counts, lambda_*).

### 5.2 99.52% undecidable — as a main result
Of the 332,571 stars, **330,984 (99.52%)** lie outside the field of every WS20 pointing[^s1]. Among them, **1,530 stars** have observation files in the BL open archive but no published limit (C/X band, or L/S/10-cm not in Price et al. 2020) and are classified as "observed, unpublished", undecidable (d)[^ph1]. Undecidable stars are tilted neither toward vacancy nor toward occupation. This number shows, star by star, **how few of the stars within 100 pc existing radio SETI non-detections actually reach**; it is the star-level version of the haystack incompleteness of Wright et al. (2018) (Figure 3).

[FIG] figs/fig3_atlas_overview.png | Figure 3: atlas overview (projection onto the Galactic plane, machine-generated from sim_display_v1). Undecidable stars in grey (thinned 1/8); stars with a T-R1 bound in the value-neutral continuous colour of the posterior at π = 10⁻²; EMBARK-reachable stars as outlines; the Sun as a star marker. Same colour discipline as the simulator. Reproduce: python3 scripts/build_paper_figs.py


[^ph1]: `docs/phase1/00-status.md` §1.3.

### 5.3 Upper-bound curves
P(occupied | D, T, π) = expit(logit π + ln Λ) is monotonic in π; for the radio bands with Λ ∈ [0.43, 0.86] the posterior is ≈ π × Λ for π ≪ 1. Figure 4 (π sweep).

[FIG] figs/fig4_pi_sweep.png | Figure 4: upper-bound curves P(occupied | D, T, π) = expit(logit π + ln Λ). Curves use the frozen-ledger Λ (min/median/max of T-R1 and T-R3); the dotted line is the prior P = π. Reproduce: python3 scripts/build_paper_figs.py
 The "vacancy" is a curve, not a single number.

### 5.4 Solar self-calibration
In the Earth-level band T-R3 the posterior ≈ the prior: the lowest technology band about which this atlas can speak is calibrated by Earth itself (§4.5).

### 5.5 The W1 information layer (claim=false)
For T-W1, derived from the WISE photometry embedded in GCNS, among the 192,363 main-sequence stars with W3/W4 photometry (3,615 detection candidates already in excess, 54,498 outside the model, and 82,094 without photometry are undecidable), 191,237 have Λ < 1 (ε > 0) at γ = 0.1 — most of them Λ = 0, i.e. a Dyson sphere would have been detected in every T_DS interval — and 1,126 are insensitive with Λ = 1[^w1]. This is physically correct: the Sun at 10 pc has a 12 µm photospheric flux of 1.9 Jy, whereas a γ = 0.1, 300 K partial Dyson sphere radiates 90 Jy. But because the G3(ii) anchor failed, this derivation carries no claim status and is provided in v1 as an information layer (off by default, with an "anchor not established" badge).

[^w1]: `data/phase2/lambda_ledger.json` (lambda_W1_g0.1). The Λ < 1 count includes stars with Λ = 0.

## 6. Three-axis atlas

### 6.1 Join rates
Reachability was imported from the EMBARK reachability atlas v1 (37,498 stars) by DR3 source_id: **14,799** are in GCNS (4.45%), the remaining 22,699 lie beyond 100 pc and are outside the population (noted only), and 317,772 GCNS stars (95.55%) are reachability-**undecidable**[^a4]. Settlement resources were imported from GCNS quantities (M_G, BP−RP, WDprob), the Mamajek colour → type classification, the NASA Exoplanet Archive (1,037 hosts, 1,545 planets), and the HWC (45 of 70 habitable-candidate rows, 35 hosts). Nothing was recomputed on any axis.

[^a4]: `data/phase4/atlas_v1_summary.json`.

### 6.2 Cross counts (no composition)
| Condition | Stars |
|---|---:|
| EMBARK flyby-reachable (any cell) ∧ T-R1 bound | **815** |
| same ∧ T-R3 bound | 108 |
| EMBARK rendezvous-reachable ∧ T-R1 bound | 311 (of 2,339 rendezvous-reachable) |
| T-R1 bound (1,554) but outside EMBARK | 739 |
| T-R1 bound ∧ S1 (FGK main sequence) / S2 (all main sequence) | 633 / 1,406 |
| T-R1 bound ∧ known planet host | 136 |
Accounting: 1,554 = 815 + 739. The distribution of Λ is the same in every EMBARK cell (the vacancy bound is set by the coverage structure of the rows and is independent of reachability). The conditional clause of every cell is attached in the atlas JSON.

### 6.3 Settlement-resource slider
S1 narrow (FGK main sequence, Mamajek classes F0–K5): 43,119 stars; S2 all main-sequence types: 283,526; S3 resource-broad (all stars): 332,571. The slider is a function selecting the displayed star set, not a criterion, and does not affect the vacancy or reachability values. Narrow habitability (liquid water, temperature) is not used as a criterion.

### 6.4 HWC cross-reference table (not a composition)
Sixteen HWC habitable-candidate hosts carry a T-R1 bound (e.g. the host of Proxima Cen b, Λ = 0.819, EMBARK-reachable; the host of Ross 128 b, Λ = 0.860, outside EMBARK). Nineteen hosts, including TRAPPIST-1, LHS 1140, and TOI-700, lie outside every radio field and are vacancy-undecidable. Being a habitable candidate and carrying a vacancy bound are independent imported quantities; the table cross-references and does not compose them.

## 7. Discussion

### 7.1 Interpretation and scope
The results of this paper are meaningful only within four limits. First, this is a survey, not a proof: evidence of absence is limited and does not prove the absence of occupation. Second, a vacancy bound is not a settlement permit: no inference of the absence of occupation, nor of the legitimacy of settlement, can be drawn from this product. Third, the HWC cross-reference table is not a composition: no quantity in this paper multiplies habitable candidacy by a vacancy bound. Fourth, 1/N and the star-level posterior are different quantities, and their numerical proximity (§4.3(c)) is coincidental. For the same reasons, the values presented here carry no meaning apart from their conditional clause (band, survey set, π); compressing them into a single number or a ranking, forming products or weighted sums across the three axes, counting undecidable stars as vacant, and using this product to justify settlement, contact, or transmission all lie outside the scope of the method. The W1 information layer has no established anchor and is not used for vacancy claims.

### 7.2 Limitations and outlook
- **Unpublished observations**: the BL open archive holds unpublished observations (C/X band etc.) of 1,530 GCNS stars; publication of limits could move them from undecidable (d) to decidable. UWL, optical lasers, and transients remain on the extension shelf.
- **Independence assumptions**: independence of f_pipe across observations is the same premise as Price et al. (2020), but correlation effects may remain outside the sensitivity range U[0.3, 0.8].
- **Re-anchoring W1**: passive (publication of a per-star Hephaistos table, or an independent anchor at DR4 v1.1).
- **DR4 merge (2026-12-02)**: the stellar basis will be replaced by DR4 and only the distance-dependent part of the ε ledger recomputed for v1.1 (synchronised with EMBARK v1.1).
- **Population horizon**: GCNS is limited to 100 pc; most of the 288,315 WS20 stars (beyond 100 pc) are outside this atlas's population.

## Appendix A — ε factor table, receiver coverage, and the common ν grid
Transcribed from §2 of the pre-registration (b) (doi:10.5281/zenodo.22067884): EIRP50, beam response, receiver coverage (L [1.10,1.20]∪[1.34,1.90], S [1.80,2.30]∪[2.36,2.80], P [2.60,3.45] GHz), common ν-grid boundaries {1.10, 1.20, 1.34, 1.80, 1.90, 2.30, 2.36, 2.60, 2.80, 3.45}, f_pipe 0.5, the 13-point f_ill grid, 20 T_DS intervals, k = 3, S/N ≥ 3.5, main-sequence selection, Mamajek table sha256 1de2edee…, WISE zero points.

## Appendix B — Method record and AI disclosure
Three roles: the human (Yukie Maeda) — direction, gate rulings, all final decisions at branch points; chat Claude — staff officer, independent recomputation (the second G2 path), literature cross-checks; Claude Code (Fable 5) — execution. Operational record: 8 rulings (#1 band set A–F; #2 pre-registration (b) revisions; #3 deviation, criterion revision; #4 acceptance of failure and demotion; #5 seven referred items; #6 approval of the outline; #7 conditional approval of report (2); #8 pre-publication style and format), 2 stops (G3(i)(b), G3(ii) — both correct, resumed by ruling), 1 deviation, 1 failed anchor, 5 self-reports (the addendum omission, the BL tally, the log path string, E-7, E-8). Error ledger r1 (E-1–E-8). This internal verification is not a substitute for human peer review.

## Appendix C — Undecidable accounting (three axes)
| Axis | Undecidable | Fraction |
|---|---:|---:|
| Vacancy (radio, three bands; outside all fields) | 330,984 | 99.52% |
| Vacancy (W1) | extension shelf (information layer) | — |
| Reachability (outside EMBARK) | 317,772 | 95.55% |
| Settlement resources (no photometry) | 8,261 | 2.48% |

## Appendix D — Reproducibility and data release
Regeneration: `python3 src/vacancy/build_ledger.py` (3 s) / Figures 1–4: `python3 scripts/build_paper_figs.py` → `scripts/export_g2.py` → `python3 src/vacancy/aggregate.py` (≈10 min) → `scripts/g3_i_ws20_price.py` / `g3_ii_hephaistos.py` / `g3_iii_solar_selftest.py` → `python3 src/vacancy/build_atlas.py`. Unit tests: `python3 -m unittest tests.test_epsilon` (14 tests). Released files: the ε ledger (`ledger_v0.json`, formula version eps-v0.2), the Λ ledger (`lambda_ledger.json`), the three-axis atlas (`atlas_v1.json`), radio-row provenance (`radio_obs_v0.json`), the G1/G2/G3 reports, frozen copies of the NEA and HWC inputs, all scripts, error ledger r1, and the SHA-256 manifest (`MANIFEST.json`). Pre-registration (a) commit 10a01e710854b69344651ed6ba016ab303c9d124; (b) doi:10.5281/zenodo.22067884.

## Acknowledgements
This work has made use of data from the European Space Agency (ESA) mission Gaia (https://www.cosmos.esa.int/gaia), processed by the Gaia Data Processing and Analysis Consortium (DPAC, https://www.cosmos.esa.int/web/gaia/dpac/consortium). Funding for the DPAC has been provided by national institutions, in particular the institutions participating in the Gaia Multilateral Agreement. This research has made use of the NASA Exoplanet Archive, which is operated by the California Institute of Technology, under contract with the National Aeronautics and Space Administration under the Exoplanet Exploration Program. This research has made use of the VizieR catalogue access tool, CDS, Strasbourg, France (DOI: 10.26093/cds/vizier). The Habitable Worlds Catalog is maintained by the Planetary Habitability Laboratory @ UPR Arecibo. Observation metadata from the Breakthrough Listen open data archive (seti.berkeley.edu/opendata) were used.

## References

- Bailer-Jones C. A. L. et al. 2018, AJ 156, 58.
- Brandt T. D. 2021, ApJS 254, 42.
- Cutri R. M. et al. 2014, VizieR On-line Data Catalog II/328.
- Enriquez J. E. et al. 2017, ApJ 849, 104.
- Gaia Collaboration 2016, A&A 595, A1.
- Gaia Collaboration 2021, A&A 649, A1.
- Gaia Collaboration 2023, A&A 674, A1.
- Gaia Collaboration, Smart R. L. et al. 2021, A&A 649, A6.
- Griffith R. L. et al. 2015, ApJS 217, 25.
- Grimaldi C. 2017, Sci. Rep. 7, 46273.
- Habitable Worlds Catalog, PHL @ UPR Arecibo (retrieved 2026-08-23).
- Isaacson H. et al. 2017, PASP 129, 054501.
- Jarrett T. H. et al. 2011, ApJ 735, 112.
- Lebofsky M. et al. 2019, PASP 131, 124505.
- Maeda Y. 2026a, Zenodo, doi:10.5281/zenodo.22067884 (pre-registration (b)).
- Maeda Y. 2026b, WAKE, Zenodo, doi:10.5281/zenodo.21966305.
- Maeda Y. 2026c, EMBARK, Zenodo, doi:10.5281/zenodo.22059576.
- Marocco F. et al. 2021, ApJS 253, 8.
- NASA Exoplanet Archive, Planetary Systems Composite Parameters, doi:10.26133/NEA12 (retrieved 2026-08-23).
- Pecaut M. J., Mamajek E. E. 2013, ApJS 208, 9.
- Price D. C. et al. 2020, AJ 159, 86.
- Saide R. C. et al. 2023, MNRAS 522, 2393.
- Sheikh S. Z. et al. 2019, ApJ 884, 14.
- Suazo M. et al. 2022, MNRAS 512, 2988.
- Suazo M. et al. 2024, MNRAS 531, 695.
- Sullivan W. T., Brown S., Wetherill C. 1978, Science 199, 377.
- Wlodarczyk-Sroka B. S., Garrett M. A., Siemion A. P. V. 2020, MNRAS 498, 5720.
- Wright E. L. et al. 2010, AJ 140, 1868.
- Wright J. T. et al. 2014a, ApJ 792, 26.
- Wright J. T. et al. 2014b, ApJ 792, 27.
- Wright J. T., Kanodia S., Lubar E. 2018, AJ 156, 260.
