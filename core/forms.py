from django import forms

class CacaPalavrasForm(forms.Form):
    col = forms.IntegerField(label='Colunas', min_value=1, max_value=40)
    lin = forms.IntegerField(label='Linhas', min_value=1, max_value=60)
    palavras = forms.CharField(label='Palavras (separadas por vírgula)', widget=forms.Textarea)
    nivel = forms.ChoiceField(label='Nível', choices=[(1, '1'), (2, '2'), (3, '3')])

    class Meta:
        fields = ['col', 'lin', 'palavras', 'nivel']