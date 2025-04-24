from django.contrib import admin
from django.contrib import admin
from .models import Categoria, Produto, Cliente, Pedido, ItemPedido, AvaliacaoProduto, Estoque, Pagamento, Promocao, Carrinho, ItemCarrinho

admin.site.register(Categoria)
admin.site.register(Produto)
admin.site.register(Cliente)
admin.site.register(Pedido)
admin.site.register(ItemPedido)
admin.site.register(AvaliacaoProduto)
admin.site.register(Estoque)
admin.site.register(Pagamento)
admin.site.register(Promocao)
admin.site.register(Carrinho)
admin.site.register(ItemCarrinho)