# Disease Reference Image Policy

This build changes disease-card images from a best-effort UI-name search to a two-stage verified reference-image system.

1. **Curated exact Commons files** are used first for classes where a file description was manually verified against the crop/disease/pathogen.
2. **Disease/pathogen-specific Wikimedia Commons resolution** is used for the remaining cards. Matching uses the full `imageQuery`, including scientific/pathogen terms, crop terms, file title, description and metadata.
3. Every displayed image includes a **Source / license** link.
4. Images are labelled **visual reference only; not proof of diagnosis**.
5. If a sufficiently matched image cannot be resolved, the UI does not substitute a generic crop photo; it gives the user a disease-specific Commons image-search link instead.

Curated exact references currently include representative verified files for Corn/Maize, Tomato, Apple, Rice, Grape, Cucumber, Lemon and Soybean. All 75 model disease/condition cards retain a disease-specific `imageQuery` for the strict resolver.
