from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class Categoria(models.Model):
    nome = models.CharField(max_length=100, verbose_name=_('Nome'))

    class Meta:
        verbose_name = _('Categoria')
        verbose_name_plural = _('Categorias')
        ordering = ['nome']

    def __str__(self):
        return self.nome

    @property
    def total_produtos(self):
        return self.produto_set.count()

    @property
    def produtos_ativos(self):
        return self.produto_set.filter(ativo=True).count()

class Produto(models.Model):
    nome = models.CharField(max_length=100, verbose_name=_('Nome do Produto'))
    descricao = models.TextField(verbose_name=_('Descrição'))
    preco = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Preço'), validators=[MinValueValidator(0.01)])
    categoria = models.ForeignKey(Categoria, on_delete=models.SET_NULL, null=True, related_name='produtos', verbose_name=_('Categoria'))
    ativo = models.BooleanField(default=True, verbose_name=_('Ativo'))
    estoque = models.IntegerField(default=0, verbose_name=_('Estoque'), validators=[MinValueValidator(0)])
    data_cadastro = models.DateTimeField(auto_now_add=True, verbose_name=_('Data de Cadastro'))
    data_atualizacao = models.DateTimeField(auto_now=True, verbose_name=_('Data de Atualização'))

    class Meta:
        verbose_name = _('Produto')
        verbose_name_plural = _('Produtos')
        ordering = ['nome']
        #index_together = [('id', 'slug')]

    def __str__(self):
        return self.nome

    @property
    def preco_formatado(self):
        return f'R$ {self.preco:.2f}'

    @property
    def em_estoque(self):
        return self.estoque > 0

class Cliente(models.Model):
    ESTADOS_BRASILEIROS = [
        ('AC', 'Acre'), ('AL', 'Alagoas'), ('AP', 'Amapá'), ('AM', 'Amazonas'), ('BA', 'Bahia'),
        ('CE', 'Ceará'), ('DF', 'Distrito Federal'), ('ES', 'Espírito Santo'), ('GO', 'Goiás'),
        ('MA', 'Maranhão'), ('MT', 'Mato Grosso'), ('MS', 'Mato Grosso do Sul'), ('MG', 'Minas Gerais'),
        ('PA', 'Pará'), ('PB', 'Paraíba'), ('PR', 'Paraná'), ('PE', 'Pernambuco'), ('PI', 'Piauí'),
        ('RJ', 'Rio de Janeiro'), ('RN', 'Rio Grande do Norte'), ('RS', 'Rio Grande do Sul'),
        ('RO', 'Rondônia'), ('RR', 'Roraima'), ('SC', 'Santa Catarina'), ('SP', 'São Paulo'),
        ('SE', 'Sergipe'), ('TO', 'Tocantins'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('Usuário'))
    endereco = models.CharField(max_length=255, verbose_name=_('Endereço'))
    cidade = models.CharField(max_length=100, verbose_name=_('Cidade'))
    estado = models.CharField(max_length=2, choices=ESTADOS_BRASILEIROS, verbose_name=_('Estado'))
    cep = models.CharField(max_length=9, verbose_name=_('CEP'))
    telefone = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('Telefone'))
    data_nascimento = models.DateField(blank=True, null=True, verbose_name=_('Data de Nascimento'))

    class Meta:
        verbose_name = _('Cliente')
        verbose_name_plural = _('Clientes')

    def __str__(self):
        return self.user.get_full_name()

    @property
    def nome_completo(self):
        return self.user.get_full_name()

    @property
    def idade(self):
        if self.data_nascimento:
            from datetime import date
            hoje = date.today()
            return hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        return None

class Pedido(models.Model):
    STATUS_PEDIDO = [
        ('pendente', _('Pendente')),
        ('processando', _('Processando')),
        ('enviado', _('Enviado')),
        ('entregue', _('Entregue')),
        ('cancelado', _('Cancelado')),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='pedidos', verbose_name=_('Cliente'))
    data_pedido = models.DateTimeField(auto_now_add=True, verbose_name=_('Data do Pedido'))
    status = models.CharField(max_length=20, choices=STATUS_PEDIDO, default='pendente', verbose_name=_('Status do Pedido'))
    total = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Total do Pedido'))
    endereco_entrega = models.CharField(max_length=255, verbose_name=_('Endereço de Entrega'))
    cep_entrega = models.CharField(max_length=9, verbose_name=_('CEP de Entrega'))

    class Meta:
        verbose_name = _('Pedido')
        verbose_name_plural = _('Pedidos')
        ordering = ['-data_pedido']

    def __str__(self):
        return f'Pedido #{self.id} - {self.cliente.user.get_full_name()}'

    @property
    def numero_itens(self):
        return self.itempedido_set.count()

    @property
    def total_formatado(self):
        return f'R$ {self.total:.2f}'

class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='itens', verbose_name=_('Pedido'))
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, verbose_name=_('Produto'))
    quantidade = models.PositiveIntegerField(default=1, verbose_name=_('Quantidade'))
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Preço Unitário'))
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Subtotal'))

    class Meta:
        verbose_name = _('Item do Pedido')
        verbose_name_plural = _('Itens do Pedido')
        unique_together = ('pedido', 'produto')

    def __str__(self):
        return f'{self.quantidade} x {self.produto.nome} no Pedido #{self.pedido.id}'

    @property
    def subtotal_formatado(self):
        return f'R$ {self.subtotal:.2f}'

    @property
    def nome_produto(self):
        return self.produto.nome

class AvaliacaoProduto(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, related_name='avaliacoes', verbose_name=_('Produto'))
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name=_('Cliente'))
    nota = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name=_('Nota'))
    comentario = models.TextField(blank=True, null=True, verbose_name=_('Comentário'))
    data_avaliacao = models.DateTimeField(auto_now_add=True, verbose_name=_('Data da Avaliação'))

    class Meta:
        verbose_name = _('Avaliação do Produto')
        verbose_name_plural = _('Avaliações dos Produtos')
        unique_together = ('produto', 'cliente')
        ordering = ['-data_avaliacao']

    def __str__(self):
        return f'Avaliação de {self.cliente.user.get_full_name()} para {self.produto.nome}'

    @property
    def nota_extenso(self):
        notas = {
            1: _('Péssimo'),
            2: _('Ruim'),
            3: _('Regular'),
            4: _('Bom'),
            5: _('Excelente'),
        }
        return notas.get(self.nota, _('Não Avaliado'))

    @property
    def nome_cliente(self):
        return self.cliente.user.get_full_name()

class Estoque(models.Model):
    produto = models.OneToOneField(Produto, on_delete=models.CASCADE, related_name='estoque_info', verbose_name=_('Produto'))
    quantidade = models.IntegerField(default=0, verbose_name=_('Quantidade em Estoque'), validators=[MinValueValidator(0)])
    ultima_atualizacao = models.DateTimeField(auto_now=True, verbose_name=_('Última Atualização'))

    class Meta:
        verbose_name = _('Estoque')
        verbose_name_plural = _('Estoques')

    def __str__(self):
        return f'Estoque de {self.produto.nome}'

    @property
    def disponivel(self):
        return self.quantidade > 0

    @property
    def precisa_reposicao(self):
        # Exemplo de lógica para verificar se precisa de reposição
        return self.quantidade < 5

class Pagamento(models.Model):
    PEDIDO_PAGO = 'pago'
    PEDIDO_PENDENTE = 'pendente'
    PEDIDO_REJEITADO = 'rejeitado'
    STATUS_PAGAMENTO_CHOICES = [
        (PEDIDO_PAGO, _('Pago')),
        (PEDIDO_PENDENTE, _('Pendente')),
        (PEDIDO_REJEITADO, _('Rejeitado')),
    ]

    pedido = models.OneToOneField(Pedido, on_delete=models.CASCADE, related_name='pagamento', verbose_name=_('Pedido'))
    data_pagamento = models.DateTimeField(auto_now_add=True, verbose_name=_('Data do Pagamento'))
    valor = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Valor Pago'))
    status = models.CharField(max_length=20, choices=STATUS_PAGAMENTO_CHOICES, default=PEDIDO_PENDENTE, verbose_name=_('Status do Pagamento'))
    metodo = models.CharField(max_length=50, verbose_name=_('Método de Pagamento'))
    transacao_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_('ID da Transação'))

    class Meta: 
        verbose_name = _('Pagamento')
        verbose_name_plural = _('Pagamentos')
        ordering = ['-data_pagamento']

    def __str__(self):
        return f'Pagamento do Pedido #{self.pedido.id} - Status: {self.get_status_display()}'

    @property
    def valor_formatado(self):
        return f'R$ {self.valor:.2f}'

    @property
    def pedido_cliente(self):
        return self.pedido.cliente.user.get_full_name()

class Promocao(models.Model):
    nome = models.CharField(max_length=100, verbose_name=_('Nome da Promoção'))
    descricao = models.TextField(blank=True, null=True, verbose_name=_('Descrição da Promoção'))
    desconto_percentual = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, validators=[MinValueValidator(0.00), MaxValueValidator(100.00)], verbose_name=_('Desconto (%)'))
    data_inicio = models.DateTimeField(verbose_name=_('Data de Início'))
    data_fim = models.DateTimeField(verbose_name=_('Data de Fim'))
    produtos = models.ManyToManyField(Produto, related_name='promocoes', blank=True, verbose_name=_('Produtos'))
    ativa = models.BooleanField(default=True, verbose_name=_('Ativa'))

    class Meta:
        verbose_name = _('Promoção')
        verbose_name_plural = _('Promoções')
        ordering = ['-data_fim', 'data_inicio']

    def __str__(self):
        return self.nome

    @property
    def desconto_formatado(self):
        return f'{self.desconto_percentual}%'

    @property
    def duracao(self):
        return self.data_fim - self.data_inicio

class Carrinho(models.Model):
    cliente = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='carrinho', verbose_name=_('Cliente'))
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name=_('Data de Criação'))
    ultima_atualizacao = models.DateTimeField(auto_now=True, verbose_name=_('Última Atualização'))

    class Meta:
        verbose_name = _('Carrinho')
        verbose_name_plural = _('Carrinhos')

    def __str__(self):
        return f'Carrinho de {self.cliente.user.get_full_name()}'

    @property
    def numero_itens(self):
        return self.itemcarrinho_set.count()

    @property
    def total_carrinho(self):
        total = 0
        for item in self.itemcarrinho_set.all():
            total += item.subtotal
        return total

class ItemCarrinho(models.Model):
    carrinho = models.ForeignKey(Carrinho, on_delete=models.CASCADE, related_name='itens', verbose_name=_('Carrinho'))
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, verbose_name=_('Produto'))
    quantidade = models.PositiveIntegerField(default=1, verbose_name=_('Quantidade'))
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Preço Unitário'))
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Subtotal'))

    class Meta:
        verbose_name = _('Item do Carrinho')
        verbose_name_plural = _('Itens do Carrinho')
        unique_together = ('carrinho', 'produto')

    def __str__(self):
        return f'{self.quantidade} x {self.produto.nome} no Carrinho de {self.carrinho.cliente.user.get_full_name()}'

    @property
    def subtotal_formatado(self):
        return f'R$ {self.subtotal:.2f}'

    @property
    def nome_produto(self):
        return self.produto.nome