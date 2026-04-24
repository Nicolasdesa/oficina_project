"""
pdf_generator.py — gera o PDF da Ordem de Serviço usando ReportLab.
"""
from io import BytesIO
from decimal import Decimal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, HRFlowable,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


# ── Paleta de cores ──────────────────────────────────────────────────────────
AZUL_ESCURO = colors.HexColor('#1F3864')
AZUL_MEDIO  = colors.HexColor('#2E75B6')
AZUL_CLARO  = colors.HexColor('#BDD7EE')
VERDE       = colors.HexColor('#375623')
VERDE_CLARO = colors.HexColor('#E2EFDA')
CINZA       = colors.HexColor('#F2F2F2')
LARANJA     = colors.HexColor('#ED7D31')
BRANCO      = colors.white
PRETO       = colors.black


def _brl(value):
    """Formata Decimal como moeda BRL."""
    try:
        return f'R$ {float(value):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    except Exception:
        return 'R$ 0,00'


def gerar_pdf_os(ordem):
    """
    Recebe uma instância de OrdemServico e retorna os bytes do PDF.
    Use assim na view:
        buffer = gerar_pdf_os(ordem)
        return HttpResponse(buffer, content_type='application/pdf')
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Estilos customizados ────────────────────────────────────────────────
    titulo_style = ParagraphStyle(
        'titulo', parent=styles['Normal'],
        fontSize=18, textColor=BRANCO, fontName='Helvetica-Bold',
        alignment=TA_CENTER, spaceAfter=2,
    )
    subtitulo_style = ParagraphStyle(
        'subtitulo', parent=styles['Normal'],
        fontSize=10, textColor=BRANCO, fontName='Helvetica',
        alignment=TA_CENTER,
    )
    secao_style = ParagraphStyle(
        'secao', parent=styles['Normal'],
        fontSize=11, textColor=BRANCO, fontName='Helvetica-Bold',
        alignment=TA_LEFT, leftIndent=6,
    )
    label_style = ParagraphStyle(
        'label', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#666666'),
        fontName='Helvetica', spaceAfter=1,
    )
    valor_style = ParagraphStyle(
        'valor', parent=styles['Normal'],
        fontSize=10, textColor=PRETO, fontName='Helvetica',
    )
    total_style = ParagraphStyle(
        'total', parent=styles['Normal'],
        fontSize=12, textColor=BRANCO, fontName='Helvetica-Bold',
        alignment=TA_RIGHT,
    )
    rodape_style = ParagraphStyle(
        'rodape', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#999999'),
        alignment=TA_CENTER,
    )

    W = doc.width  # largura útil

    # ── CABEÇALHO ───────────────────────────────────────────────────────────
    cabecalho = Table(
        [[
            Paragraph('🔧 OFICINA — ORDEM DE SERVIÇO', titulo_style),
            Paragraph(f'<b>{ordem.numero_os or f"OS-{ordem.pk:05d}"}</b>', titulo_style),
        ]],
        colWidths=[W * 0.7, W * 0.3],
    )
    cabecalho.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), AZUL_ESCURO),
        ('ALIGN',      (1, 0), (1, 0),  'RIGHT'),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING',   (0, 0), (-1, -1), 10),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
    ]))
    story.append(cabecalho)
    story.append(Spacer(1, 8))

    # ── STATUS BADGE ────────────────────────────────────────────────────────
    status_cores = {
        'Concluído':       colors.HexColor('#C6EFCE'),
        'Em andamento':    colors.HexColor('#FFEB9C'),
        'Aguardando peça': colors.HexColor('#FFC7CE'),
        'Cancelado':       colors.HexColor('#D9D9D9'),
    }
    status_texto_cores = {
        'Concluído':       VERDE,
        'Em andamento':    colors.HexColor('#9C5700'),
        'Aguardando peça': colors.HexColor('#9C0006'),
        'Cancelado':       colors.HexColor('#595959'),
    }
    sc = status_cores.get(ordem.status, CINZA)
    stc = status_texto_cores.get(ordem.status, PRETO)

    status_ps = ParagraphStyle('st', fontSize=10, textColor=stc,
                                fontName='Helvetica-Bold', alignment=TA_CENTER)
    status_table = Table(
        [[Paragraph(f'Status: {ordem.status}', status_ps)]],
        colWidths=[W],
    )
    status_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), sc),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 10))

    # ── SEÇÃO: DADOS DO CLIENTE ─────────────────────────────────────────────
    def secao_header(texto):
        t = Table([[Paragraph(texto, secao_style)]], colWidths=[W])
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), AZUL_MEDIO),
            ('TOPPADDING',    (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        return t

    def campo(label, valor):
        return [
            Paragraph(label, label_style),
            Paragraph(str(valor) if valor else '—', valor_style),
        ]

    story.append(secao_header('DADOS DO CLIENTE'))
    story.append(Spacer(1, 4))

    cliente = ordem.cliente
    dados_cliente = Table(
        [
            [*campo('NOME', cliente.nome),
             *campo('TELEFONE', cliente.telefone)],
            [*campo('CPF / CNPJ', cliente.cpf_cnpj),
             *campo('E-MAIL', cliente.email)],
            [*campo('ENDEREÇO', cliente.endereco), '', ''],
        ],
        colWidths=[W * 0.12, W * 0.38, W * 0.12, W * 0.38],
    )
    dados_cliente.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), CINZA),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('SPAN', (0, 2), (3, 2)),
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, colors.HexColor('#CCCCCC')),
    ]))
    story.append(dados_cliente)
    story.append(Spacer(1, 8))

    # ── SEÇÃO: DADOS DO VEÍCULO ─────────────────────────────────────────────
    story.append(secao_header('DADOS DO VEÍCULO'))
    story.append(Spacer(1, 4))

    veiculo = ordem.veiculo
    dados_veiculo = Table(
        [
            [*campo('VEÍCULO', veiculo.descricao),
             *campo('PLACA', veiculo.placa)],
            [*campo('ANO', veiculo.ano),
             *campo('COR', veiculo.cor)],
        ],
        colWidths=[W * 0.12, W * 0.38, W * 0.12, W * 0.38],
    )
    dados_veiculo.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), CINZA),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, colors.HexColor('#CCCCCC')),
    ]))
    story.append(dados_veiculo)
    story.append(Spacer(1, 8))

    # ── SEÇÃO: DATAS ─────────────────────────────────────────────────────────
    story.append(secao_header('DATAS'))
    story.append(Spacer(1, 4))

    fmt = lambda d: d.strftime('%d/%m/%Y %H:%M') if d else '—'
    datas_table = Table(
        [[
            *campo('ENTRADA', fmt(ordem.data_entrada)),
            *campo('SAÍDA',   fmt(ordem.data_saida)),
        ]],
        colWidths=[W * 0.12, W * 0.38, W * 0.12, W * 0.38],
    )
    datas_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CINZA),
        ('TOPPADDING',    (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
    ]))
    story.append(datas_table)
    story.append(Spacer(1, 8))

    # ── SEÇÃO: DESCRIÇÃO DO SERVIÇO ──────────────────────────────────────────
    story.append(secao_header('DESCRIÇÃO DO SERVIÇO'))
    story.append(Spacer(1, 4))

    desc_style = ParagraphStyle('desc', fontSize=10, fontName='Helvetica',
                                 leading=14, leftIndent=6, rightIndent=6)
    desc_table = Table(
        [[Paragraph(ordem.descricao_servico, desc_style)]],
        colWidths=[W],
    )
    desc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), CINZA),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(desc_table)
    story.append(Spacer(1, 8))

    # ── SEÇÃO: PEÇAS UTILIZADAS ──────────────────────────────────────────────
    itens_peca = list(ordem.itens_peca.select_related('peca').all())
    if itens_peca:
        story.append(secao_header('PEÇAS UTILIZADAS'))
        story.append(Spacer(1, 4))

        th_style = ParagraphStyle('th', fontSize=9, textColor=BRANCO,
                                   fontName='Helvetica-Bold', alignment=TA_CENTER)
        td_style = ParagraphStyle('td', fontSize=9, fontName='Helvetica')
        td_right = ParagraphStyle('tdr', fontSize=9, fontName='Helvetica', alignment=TA_RIGHT)

        header_pecas = [
            Paragraph('Descrição', th_style),
            Paragraph('Código', th_style),
            Paragraph('Qtd', th_style),
            Paragraph('Valor Unit.', th_style),
            Paragraph('Subtotal', th_style),
        ]
        rows_pecas = [header_pecas]
        for ip in itens_peca:
            rows_pecas.append([
                Paragraph(ip.peca.descricao, td_style),
                Paragraph(ip.peca.codigo or '—', td_style),
                Paragraph(str(ip.quantidade), td_style),
                Paragraph(_brl(ip.valor_unitario), td_right),
                Paragraph(_brl(ip.subtotal), td_right),
            ])

        t_pecas = Table(rows_pecas, colWidths=[W*0.36, W*0.16, W*0.08, W*0.18, W*0.18])
        t_pecas.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), AZUL_CLARO),
            ('TEXTCOLOR',     (0, 0), (-1, 0), AZUL_ESCURO),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BRANCO, CINZA]),
            ('GRID',          (0, 0), (-1, -1), 0.3, colors.HexColor('#CCCCCC')),
            ('TOPPADDING',    (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING',   (0, 0), (-1, -1), 6),
            ('ALIGN',         (2, 1), (-1, -1), 'RIGHT'),
        ]))
        story.append(t_pecas)
        story.append(Spacer(1, 8))

    # ── SEÇÃO: MÃO DE OBRA ───────────────────────────────────────────────────
    itens_mo = list(ordem.itens_mo.select_related('mecanico').all())
    if itens_mo:
        story.append(secao_header('MÃO DE OBRA'))
        story.append(Spacer(1, 4))

        header_mo = [
            Paragraph('Mecânico', th_style),
            Paragraph('Serviço', th_style),
            Paragraph('Horas', th_style),
            Paragraph('Valor/Hora', th_style),
            Paragraph('Subtotal', th_style),
        ]
        rows_mo = [header_mo]
        for im in itens_mo:
            rows_mo.append([
                Paragraph(im.mecanico.nome, td_style),
                Paragraph(im.tipo_servico, td_style),
                Paragraph(str(im.horas_trabalhadas), td_style),
                Paragraph(_brl(im.valor_hora), td_right),
                Paragraph(_brl(im.subtotal), td_right),
            ])

        t_mo = Table(rows_mo, colWidths=[W*0.24, W*0.28, W*0.10, W*0.18, W*0.18])
        t_mo.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), AZUL_CLARO),
            ('TEXTCOLOR',     (0, 0), (-1, 0), AZUL_ESCURO),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [BRANCO, CINZA]),
            ('GRID',          (0, 0), (-1, -1), 0.3, colors.HexColor('#CCCCCC')),
            ('TOPPADDING',    (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING',   (0, 0), (-1, -1), 6),
            ('ALIGN',         (2, 1), (-1, -1), 'RIGHT'),
        ]))
        story.append(t_mo)
        story.append(Spacer(1, 8))

    # ── TOTAIS ───────────────────────────────────────────────────────────────
    total_label = ParagraphStyle('tl', fontSize=10, fontName='Helvetica',
                                  alignment=TA_RIGHT, textColor=PRETO)
    total_valor = ParagraphStyle('tv', fontSize=10, fontName='Helvetica-Bold',
                                  alignment=TA_RIGHT, textColor=PRETO)

    totais_data = [
        [Paragraph('Total em Peças:', total_label),
         Paragraph(_brl(ordem.total_pecas), total_valor)],
        [Paragraph('Total Mão de Obra:', total_label),
         Paragraph(_brl(ordem.total_mao_obra), total_valor)],
    ]
    t_totais = Table(totais_data, colWidths=[W * 0.78, W * 0.22])
    t_totais.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), CINZA),
        ('TOPPADDING',    (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, colors.HexColor('#CCCCCC')),
    ]))
    story.append(t_totais)

    # Total Geral — destaque laranja
    total_geral_ps = ParagraphStyle('tg', fontSize=13, fontName='Helvetica-Bold',
                                     textColor=BRANCO, alignment=TA_RIGHT)
    tg_table = Table(
        [[Paragraph(f'TOTAL GERAL:   {_brl(ordem.total_geral)}', total_geral_ps)]],
        colWidths=[W],
    )
    tg_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), LARANJA),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
    ]))
    story.append(tg_table)
    story.append(Spacer(1, 10))

    # ── OBSERVAÇÕES ──────────────────────────────────────────────────────────
    if ordem.observacoes:
        story.append(secao_header('OBSERVAÇÕES'))
        story.append(Spacer(1, 4))
        obs_table = Table(
            [[Paragraph(ordem.observacoes, desc_style)]],
            colWidths=[W],
        )
        obs_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#FFFDE7')),
            ('TOPPADDING',    (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#F9A825')),
        ]))
        story.append(obs_table)
        story.append(Spacer(1, 10))

    # ── ASSINATURAS ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 20))
    assin_style = ParagraphStyle('assin', fontSize=9, alignment=TA_CENTER,
                                  textColor=colors.HexColor('#555555'))
    assin = Table(
        [[
            Paragraph('_______________________________<br/>Responsável pela Oficina', assin_style),
            Paragraph('_______________________________<br/>Assinatura do Cliente', assin_style),
        ]],
        colWidths=[W * 0.5, W * 0.5],
    )
    story.append(assin)
    story.append(Spacer(1, 10))

    # ── RODAPÉ ───────────────────────────────────────────────────────────────
    story.append(HRFlowable(width=W, color=AZUL_CLARO, thickness=0.5))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f'Documento gerado pelo Sistema de Gestão de Oficina  •  {ordem.numero_os or f"OS-{ordem.pk:05d}"}',
        rodape_style,
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
