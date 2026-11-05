"""Seed missing Markdown files in data/datasheets/ from the curated starter set.

Existing files are preserved. This script does not fetch or independently verify sources.
"""
from pathlib import Path

DATASHEETS = {
    "apple_iphone_13.md": """# Apple iPhone 13 — Hardware & Specification Datasheet

**Brand:** Apple  
**Model:** iPhone 13  
**Variant:** Base  
**Model Identifiers:** A2482, A2631, A2633, A2634, A2635  
**Release Year:** 2021  
**Source Title:** Apple iPhone 13 Repair Manual  
**Source URL:** https://support.apple.com/en-us/100402  
**Date Verified:** 2026-11-05  
**Ingress Protection:** IP68 (IEC standard 60529, maximum depth of 6m up to 30 min)  

---

## 1. Safety & Device Disclaimers
- Source: Apple iPhone 13 Repair Manual (Safety Overview)
- Reference: https://support.apple.com/en-us/100402
- Swollen, dented, or leaking lithium-ion batteries represent an immediate safety hazard and must be handled only by qualified technicians with specialized containment equipment.
- Ingress protection (IP68) water and dust resistance is compromised whenever the device enclosure is opened.

## 2. Display & Screen Specifications
- Source: Apple iPhone 13 Repair Manual & Technical Specifications
- Reference: https://support.apple.com/en-us/100402
- Panel Type: 6.1-inch Super Retina XDR OLED display (2532 x 1170 pixels at 460 ppi, 60Hz refresh rate).
- Glass Protection: Ceramic Shield front cover.
- Architecture: Fused OLED display and touch digitizer assembly.
- Software Calibration: Replacement displays require post-service System Configuration via Apple Diagnostics to calibrate True Tone and ambient light sensors.

## 3. Battery & Power System
- Source: Apple iPhone 13 Repair Manual
- Reference: https://support.apple.com/en-us/100402
- Capacity: 3,240 mAh (12.41 Wh) Lithium-ion cell, nominal voltage 3.83V.
- Internal Mounting: Secured with stretch-release adhesive pull-tabs.
- Replacement Requirement: Factory adhesive must be replaced whenever the battery is unseated.

## 4. Charging & Port Architecture
- Source: Apple iPhone 13 Repair Manual
- Reference: https://support.apple.com/en-us/100402
- Port Interface: Proprietary Lightning dock connector.
- Component Design: The Lightning charging port is integrated onto the lower dock flex assembly along with the primary microphone and antenna connections.
- Wireless Interface: Supports Qi wireless charging and MagSafe magnetic inductive charging up to 15W.
""",

    "apple_iphone_13_pro.md": """# Apple iPhone 13 Pro — Hardware & Specification Datasheet

**Brand:** Apple  
**Model:** iPhone 13 Pro  
**Variant:** Pro  
**Model Identifiers:** A2483, A2636, A2638, A2639, A2640  
**Release Year:** 2021  
**Source Title:** Apple iPhone 13 Pro Repair Manual  
**Source URL:** https://support.apple.com/en-us/100416  
**Date Verified:** 2026-11-05  
**Ingress Protection:** IP68 (IEC standard 60529, maximum depth of 6m up to 30 min)  

---

## 1. Safety & Device Disclaimers
- Source: Apple iPhone 13 Pro Repair Manual (Safety Overview)
- Reference: https://support.apple.com/en-us/100416
- Swollen, dented, or punctured batteries require professional technician escalation.
- Enclosure opening breaks factory liquid seals; requires new pressure gasket during reassembly.

## 2. Display & Screen Specifications
- Source: Apple iPhone 13 Pro Repair Manual & Technical Specifications
- Reference: https://support.apple.com/en-us/100416
- Panel Type: 6.1-inch Super Retina XDR OLED with ProMotion technology (10Hz–120Hz adaptive refresh rate, 2532 x 1170 pixels at 460 ppi).
- Glass Protection: Ceramic Shield front cover, surgical-grade stainless steel frame.
- Calibration: Requires Apple Diagnostics System Configuration to preserve 120Hz ProMotion and True Tone.

## 3. Battery & Power System
- Source: Apple iPhone 13 Pro Repair Manual
- Reference: https://support.apple.com/en-us/100416
- Capacity: 3,095 mAh (11.97 Wh) Lithium-ion cell.
- Internal Mounting: Secured with stretch-release adhesive pull-tabs.

## 4. Charging & Port Architecture
- Source: Apple iPhone 13 Pro Repair Manual
- Reference: https://support.apple.com/en-us/100416
- Port Interface: Lightning dock connector integrated on lower flex assembly.
- Additional Hardware: Includes LiDAR scanner and optical image stabilization (sensor-shift) on telephoto module.
""",

    "samsung_galaxy_a51.md": """# Samsung Galaxy A51 — Hardware & Specification Datasheet

**Brand:** Samsung  
**Model:** Galaxy A51  
**Variant:** 4G Standard  
**Model Identifiers:** SM-A515F, SM-A515FN, SM-A515G  
**Release Year:** 2020  
**Source Title:** Samsung Service Documentation & iFixit Teardown  
**Source URL:** https://www.ifixit.com/Device/Samsung_Galaxy_A51  
**Date Verified:** 2026-11-05  
**Ingress Protection:** No official IP rating (water-permeable enclosure)  

---

## 1. Safety & Device Disclaimers
- Source: Samsung Service Documentation & iFixit
- Reference: https://www.ifixit.com/Device/Samsung_Galaxy_A51
- Li-Po pouch cells are susceptible to thermal runaway if bent or punctured with tools.
- Device has no liquid seals; liquid ingress warrants immediate power-off and professional drying.

## 2. Display & Screen Specifications
- Source: Samsung Official Specifications & iFixit
- Reference: https://www.ifixit.com/Device/Samsung_Galaxy_A51
- Panel Type: 6.5-inch Super AMOLED (1080 x 2400 pixels, 20:9 ratio, 60Hz refresh rate).
- Glass Protection: Corning Gorilla Glass 3.
- Architecture: Fused AMOLED and digitizer bonded to front plastic midframe.
- Fingerprint Sensor: In-display optical fingerprint scanner located beneath the display matrix.

## 3. Battery & Power System
- Source: Samsung Service Documentation (Battery Spec)
- Reference: https://www.ifixit.com/Device/Samsung_Galaxy_A51
- Capacity: 4,000 mAh (15.4 Wh) Lithium-Polymer, Model identifier **EB-BA515ABY**.
- Nominal Voltage: 3.85V, Charge Voltage: 4.4V.
- Internal Mounting: Affixed with permanent double-sided adhesive tape (no stretch pull-tabs).

## 4. Charging & Port Architecture
- Source: iFixit Samsung Galaxy A51 Sub-PBA Teardown
- Reference: https://www.ifixit.com/Device/Samsung_Galaxy_A51
- Port Interface: USB Type-C 2.0 with 15W Adaptive Fast Charging.
- Modularity Status: Modular daughterboard (**Sub-PBA**). The USB-C port, 3.5mm audio jack, and lower microphone are mounted on a separate board connected to the mainboard via a flexible interconnect ribbon.
- Serviceability: USB-C port repair does not require motherboard soldering; the daughterboard can be independently replaced.
""",

    "samsung_galaxy_a55.md": """# Samsung Galaxy A55 5G — Hardware & Specification Datasheet

**Brand:** Samsung  
**Model:** Galaxy A55 5G  
**Variant:** 5G  
**Model Identifiers:** SM-A556B, SM-A556E  
**Release Year:** 2024  
**Source Title:** Samsung Official Specifications & iFixit Teardown  
**Source URL:** https://www.ifixit.com/Device/Samsung_Galaxy_A55  
**Date Verified:** 2026-11-05  
**Ingress Protection:** IP67 (dust tight, water immersion up to 1m for 30 minutes)  

---

## 1. Safety & Device Disclaimers
- Source: Samsung Technical Specifications
- Reference: https://www.ifixit.com/Device/Samsung_Galaxy_A55
- Disassembly breaks the factory IP67 environmental seal; requires replacement perimeter gasket.

## 2. Display & Screen Specifications
- Source: Samsung Official Specifications
- Reference: https://www.ifixit.com/Device/Samsung_Galaxy_A55
- Panel Type: 6.6-inch Super AMOLED, 120Hz refresh rate, HDR10+, 1000 nits (HBM). Resolution: 1080 x 2340 pixels.
- Glass Protection: Corning Gorilla Glass Victus+ front and back, aluminum frame.

## 3. Battery & Power System
- Source: Samsung Service Documentation
- Reference: https://www.ifixit.com/Device/Samsung_Galaxy_A55
- Capacity: 5,000 mAh (19.25 Wh) Lithium-ion cell, Model identifier **WT-S-N28 / EB-BA556ABY**.
- Charging: Supports 25W Super Fast Charging.
- Internal Mounting: Integrated pull-pouch battery removal mechanism.

## 4. Charging & Thermal Architecture
- Source: Samsung Service Documentation & iFixit
- Reference: https://www.ifixit.com/Device/Samsung_Galaxy_A55
- Port Interface: USB Type-C 2.0 with perimeter silicone sealing gasket.
- Thermal Management: 74% larger integrated vapor chamber compared to Galaxy A54.
- Modularity Status: Modular lower sub-board with gasket seals.
""",

    "google_pixel_8a.md": """# Google Pixel 8a — Hardware & Specification Datasheet

**Brand:** Google  
**Model:** Pixel 8a  
**Variant:** Standard  
**Model Identifiers:** G8HH4, GKV4X  
**Release Year:** 2024  
**Source Title:** Google Official Pixel Phone Repair Documentation  
**Source URL:** https://support.google.com/pixelphone/answer/14257407?hl=en  
**Date Verified:** 2026-11-05  
**Ingress Protection:** IP67 (IEC standard 60529)  

---

## 1. Safety & Device Disclaimers
- Source: Google Pixel Repair Documentation
- Reference: https://support.google.com/pixelphone/answer/14257407?hl=en
- Google official guidance notes that device repair requires appropriate technical expertise; improper service risks thermal hazard or compromised ingress seals.

## 2. Display & Screen Specifications
- Source: Google Official Specifications & Repair Documentation
- Reference: https://support.google.com/pixelphone/answer/14257407?hl=en
- Panel Type: 6.1-inch Actua OLED display, up to 120Hz refresh rate, 1400 nits (HBM), 2000 nits peak. Resolution: 1080 x 2400 pixels (430 ppi).
- Glass Protection: Corning Gorilla Glass 3.
- Disassembly Architecture: Front-entry opening design (display assembly separates from front, rather than rear cover removal).
- Software Calibration: Fingerprint sensor requires software calibration via the official Google Pixel Update and Software Repair tool (`pixelrepair.withgoogle.com`).

## 3. Battery & Power System
- Source: Google Pixel Official Technical Documentation
- Reference: https://support.google.com/pixelphone/answer/14257407?hl=en
- Capacity: 4,492 mAh (17.43 Wh) Lithium-ion cell, nominal voltage 3.89V.
- Internal Mounting: Pre-installed stretch-release adhesive pull tabs.

## 4. Charging & Port Architecture
- Source: Google Pixel Specifications
- Reference: https://support.google.com/pixelphone/answer/14257407?hl=en
- Port Interface: USB Type-C 3.2 Gen 2, supporting 18W wired fast charging and Qi wireless charging.
- Modularity Status: Port is integrated with protective moisture-sensing circuitry.
""",

    "xiaomi_redmi_note_13_4g.md": """# Xiaomi Redmi Note 13 4G — Hardware & Specification Datasheet

**Brand:** Xiaomi  
**Model:** Redmi Note 13 4G  
**Variant:** 4G  
**Model Identifiers:** 23129RAA4G  
**Release Year:** 2024  
**Source Title:** Xiaomi Official Specifications (Redmi Note 13 4G)  
**Source URL:** https://www.mi.com/my/product/redmi-note-13/specs/  
**Date Verified:** 2026-11-05  
**Ingress Protection:** IP54 (splash and dust protection)  

---

## 1. Safety & Device Disclaimers
- Source: Xiaomi Official Documentation
- Reference: https://www.mi.com/my/product/redmi-note-13/specs/
- High-capacity lithium-polymer cells must be disconnected before servicing internal flex cables.

## 2. Display & Screen Specifications
- Source: Xiaomi Official Specifications
- Reference: https://www.mi.com/my/product/redmi-note-13/specs/
- Panel Type: 6.67-inch AMOLED display, 120Hz refresh rate, 1800 nits peak brightness. Resolution: 2400 x 1080 pixels (395 ppi).
- Glass Protection: **Corning Gorilla Glass 3**.
- Fingerprint Sensor: **In-display optical fingerprint sensor**.

## 3. Battery & Power System
- Source: Xiaomi Official Specifications & Spare Parts Manual
- Reference: https://www.mi.com/my/product/redmi-note-13/specs/
- Capacity: 5,000 mAh (typ) Lithium-Polymer, Model identifier **BN5M**.
- Charging: Supports 33W wired Fast Charging.
- Internal Mounting: Equipped with dual stretch pull-tabs (Tab A / Tab B).

## 4. Charging & Port Architecture
- Source: iFixit & Xiaomi Service Documentation
- Reference: https://www.ifixit.com/Device/Xiaomi_Redmi_Note_13_4G
- Port Interface: USB Type-C 2.0 with 3.5mm headphone jack.
- Modularity Status: Modular lower daughterboard (**Sub-PBA**). The USB-C port is mounted on a separate PCB connected via FPC ribbon to the main logic board.
- Serviceability: Port replacement does not require mainboard soldering.
""",

    "xiaomi_redmi_note_13_5g.md": """# Xiaomi Redmi Note 13 5G — Hardware & Specification Datasheet

**Brand:** Xiaomi  
**Model:** Redmi Note 13 5G  
**Variant:** 5G  
**Model Identifiers:** 2312DRAABG  
**Release Year:** 2024  
**Source Title:** Xiaomi Official Specifications (Redmi Note 13 5G)  
**Source URL:** https://www.mi.com/in/product/redmi-note-13-5g/specs/  
**Date Verified:** 2026-11-05  
**Ingress Protection:** IP54 (splash and dust protection)  

---

## 1. Safety & Device Disclaimers
- Source: Xiaomi Official Specifications
- Reference: https://www.mi.com/in/product/redmi-note-13-5g/specs/
- Li-Po battery safety precautions apply; do not apply mechanical force to battery casing.

## 2. Display & Screen Specifications
- Source: Xiaomi Official Specifications
- Reference: https://www.mi.com/in/product/redmi-note-13-5g/specs/
- Panel Type: 6.67-inch AMOLED display, 120Hz refresh rate, 1000 nits peak brightness. Resolution: 2400 x 1080 pixels (395 ppi).
- Glass Protection: **Corning Gorilla Glass 5** (distinct from 4G model's Gorilla Glass 3).
- Fingerprint Sensor: **Side-mounted fingerprint sensor** integrated into the power button (distinct from 4G in-display sensor).

## 3. Battery & Power System
- Source: Xiaomi Official Specifications & Spare Parts Manual
- Reference: https://www.mi.com/in/product/redmi-note-13-5g/specs/
- Capacity: 5,000 mAh (typ) Lithium-Polymer, Model identifier **BN5N**.
- Charging: Supports 33W wired Fast Charging.
- Internal Mounting: Equipped with dual stretch pull-tabs.

## 4. Charging & Port Architecture
- Source: iFixit & Xiaomi Service Documentation
- Reference: https://www.ifixit.com/Device/Xiaomi_Redmi_Note_13_5G
- Port Interface: USB Type-C 2.0 with 3.5mm headphone jack.
- Modularity Status: Modular lower daughterboard (**Sub-PBA**).
- Serviceability: Independently replaceable charging sub-board.
"""
}


def ingest_datasheets() -> None:
    output_dir = Path(__file__).resolve().parent.parent / "data" / "datasheets"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Ingesting {len(DATASHEETS)} datasheets into {output_dir}...")
    for filename, content in DATASHEETS.items():
        file_path = output_dir / filename
        if file_path.exists():
            print(f"  [SKIP] {filename} already exists; existing files are never replaced")
            continue
        file_path.write_text(content.strip() + "\n", encoding="utf-8")
        print(f"  [SAVED] {filename} ({len(content.splitlines())} lines)")
    print("Ingestion complete!")


if __name__ == "__main__":
    ingest_datasheets()
