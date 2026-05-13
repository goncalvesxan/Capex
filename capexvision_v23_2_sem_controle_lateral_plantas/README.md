# CapexVision V23.2 — Sem Controle Lateral de Plantas

Correção:
- removido o controle antigo de Plantas por unidade da barra lateral;
- mantida a aba oficial **Empresas & Plantas** para cadastrar imagens;
- vínculo das imagens permanece pelo campo `empresa`;
- ao mudar o filtro Empresa, a planta muda automaticamente;
- mantidas as configurações explicadas e o motor parametrizável.

## Rodar

```powershell
pip install -r requirements.txt
python -m streamlit run app.py
```
