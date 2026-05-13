# CapexVision V21.5 — NameError Fix

Correções definitivas:
- RISK_COLOR_MAP definido no escopo global;
- RISK_ORDER definido no escopo global;
- STATUS_COLOR_MAP definido no escopo global;
- imports reconstruídos corretamente;
- sintaxe validada;
- requirements revisado.

Depois de subir no GitHub:
1. Commit
2. Push origin
3. No Streamlit Cloud: Manage app → Clear cache → Reboot app

## Rodar local

```powershell
pip install -r requirements.txt
python -m streamlit run app.py
```
