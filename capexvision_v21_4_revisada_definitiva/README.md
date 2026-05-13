# CapexVision V21.4 — Revisada Definitiva

Correções aplicadas:
- imports reconstruídos do zero;
- erro de sintaxe removido;
- Plotly incluído no requirements.txt;
- fallback automático para instalar Plotly caso o Streamlit Cloud não leia o requirements corretamente;
- runtime Python 3.11 definido;
- versão pronta para substituir o projeto inteiro no GitHub.

## Instalação local

```powershell
pip install -r requirements.txt
python -m streamlit run app.py
```

## Streamlit Cloud

Depois de subir no GitHub:

1. Manage app
2. Settings
3. Clear cache
4. Reboot app

Se o app estiver dentro de uma pasta, confirme se o **Main file path** aponta para:

```text
app.py
```

ou, se estiver em subpasta:

```text
nome_da_pasta/app.py
```
