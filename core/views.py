import random
from django.views.generic.edit import FormView
from django.urls import reverse_lazy

from core.forms import CacaPalavrasForm


class Home(FormView):
    template_name = "index.html"
    form_class = CacaPalavrasForm
    success_url = reverse_lazy('cacapalavras')

    def form_valid(self, form):
        col = form.cleaned_data['col']
        lin = form.cleaned_data['lin']
        self.palavras = form.cleaned_data['palavras']
        palavras = self.palavras.split(',')
        nivel = form.cleaned_data['nivel']
        caca_palavras = CacaPalavras(col, lin, palavras, nivel)
        self.matriz = caca_palavras.get_matriz_final()
        return self.render_to_response(self.get_context_data(form=form, tabela=self.matriz))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'matriz'):
            context['tabela'] = self.matriz
            context['palavras'] = self.palavras
        else:
            # Matriz vazia inicial, como antes
            context['tabela'] = [['-' for _ in range(10)] for _ in range(5)]
        return context


class CacaPalavras:
    def __init__(self, col, lin, palavras, nivel):
        self.validar_quant_lin_col(lin, col)
        self.col = col
        self.lin = lin
        # Normaliza as palavras (remove espaços e acentos)
        self.palavras = [self.normalizar_string(p.replace(" ", "")) for p in palavras]
        self.nivel = int(nivel)
        self.palavras_invalidas = 0
        self.horiz = 0
        self.vert = 0
        self.diag = 0  # Contador para nível 3

        # Iniciar matriz vazia preenchida com strings vazias
        self.matriz = [["" for _ in range(col)] for _ in range(lin)]

        self.inserir_palavras()

    def normalizar_string(self, texto):
        """Versão simplificada do html_scape do PHP"""
        texto = texto.upper()
        substituicoes = {
            'Á': 'A', 'À': 'A', 'Ã': 'A', 'Â': 'A', 'Ä': 'A',
            'Õ': 'O', 'Ò': 'O', 'Ó': 'O', 'È': 'E', 'É': 'E',
            'Ê': 'E', 'Ë': 'E', 'Ì': 'I', 'Í': 'I', 'Ï': 'I', 'Ú': 'U'
        }
        for busca, troca in substituicoes.items():
            texto = texto.replace(busca, troca)
        return texto

    def validar_quant_lin_col(self, lin, col):
        """Valida se o tamanho está dentro do limite permitido"""
        if lin > 60 or col > 40:
            raise ValueError("Tamanho máximo permitido 40x60")

    def validar_tamanho_palavras(self):
        """Verifica se as palavras cabem na grade"""
        for p in self.palavras:
            if len(p) > self.col and len(p) > self.lin:
                self.palavras_invalidas += 1

    def inserir_palavras(self):
        self.validar_tamanho_palavras()
        if self.palavras_invalidas == 0:
            for palavra in self.palavras:
                # Gerencia a lógica de acordo com o nível selecionado
                if self.nivel == 1:
                    self.posicionar_palavra(palavra, inverter=False, diagonal=False)
                elif self.nivel == 2:
                    # Nível 2: Algumas palavras podem vir invertidas
                    deve_inverter = random.choice([True, False])
                    self.posicionar_palavra(palavra, inverter=deve_inverter, diagonal=False)
                elif self.nivel == 3:
                    # Nível 3: Pode ser horizontal, vertical, diagonal e/ou invertida
                    deve_inverter = random.choice([True, False])
                    deve_diagonal = random.choice([True, False])
                    self.posicionar_palavra(palavra, inverter=deve_inverter, diagonal=deve_diagonal)

    def posicionar_palavra(self, palavra, inverter=False, diagonal=False):
        p = palavra[::-1] if inverter else palavra

        # Define direções: 1=Horiz, 2=Vert, 3=Diag
        if diagonal:
            direcao = 3
        else:
            hv = random.randint(1, 2)
            direcao = self.definir_direcao_balanceada(hv)

        # Tentativas de posicionamento
        tentativas = 0
        while tentativas < 100:
            x = random.randint(0, self.lin - 1)
            y = random.randint(0, self.col - 1)

            if self.validar_local(x, y, direcao, p):
                for i, letra in enumerate(p):
                    if direcao == 1:  # Horizontal
                        self.matriz[x][y + i] = letra
                    elif direcao == 2:  # Vertical
                        self.matriz[x + i][y] = letra
                    elif direcao == 3:  # Diagonal
                        self.matriz[x + i][y + i] = letra

                # Incrementa contadores para balanceamento
                if direcao == 1:
                    self.horiz += 1
                elif direcao == 2:
                    self.vert += 1
                else:
                    self.diag += 1
                return True
            tentativas += 1
        return False

    def definir_direcao_balanceada(self, hv):
        """Garante que haja uma distribuição entre horizontal e vertical"""
        limite = len(self.palavras) // 2
        if hv == 2 and self.vert >= limite:
            return 1
        elif hv == 1 and self.horiz >= limite:
            return 2
        return hv

    def validar_local(self, x, y, direcao, p):
        tam = len(p)
        if direcao == 1:  # Horizontal
            if y + tam > self.col: return False
            return all(self.matriz[x][y + i] in ("", p[i]) for i in range(tam))

        elif direcao == 2:  # Vertical
            if x + tam > self.lin: return False
            return all(self.matriz[x + i][y] in ("", p[i]) for i in range(tam))

        elif direcao == 3:  # Diagonal
            if (x + tam > self.lin) or (y + tam > self.col): return False
            return all(self.matriz[x + i][y + i] in ("", p[i]) for i in range(tam))

        return False

    def get_matriz_final(self):
        """Preenche espaços vazios com letras aleatórias e retorna a matriz"""
        alfabeto = "ABCÇDEFGHIJKLMNOPQRSTUVWXYZ"
        for i in range(self.lin):
            for j in range(self.col):
                if self.matriz[i][j] == "":
                    self.matriz[i][j] = random.choice(alfabeto)
        return self.matriz