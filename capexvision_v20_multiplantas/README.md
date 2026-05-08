# CapexVision V20 — Multi Plantas por Unidade

Correções e melhorias:
- Corrige imagem aparecendo como código;
- Permite cadastrar mais de uma imagem de planta;
- Cada imagem é vinculada a uma unidade/localização;
- Quando o filtro Unidade / Localização muda, a imagem da planta muda junto;
- Hotspots continuam sobre a imagem;
- Configurações mostra as plantas cadastradas.

## Como usar

1. No menu lateral, vá em **Plantas por unidade**.
2. Cadastre as unidades no campo separado por `;`.
3. Escolha uma unidade.
4. Faça upload da imagem PNG/JPG/JPEG.
5. Troque o filtro **Unidade / Localização** na tela principal.
6. A planta exibida será a imagem vinculada à unidade selecionada.

## Rodar

```powershell
pip install -r requirements.txt
python -m streamlit run app.py
```
