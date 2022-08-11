from ObjetoTS import *
import xml.etree.ElementTree as ET

# Recebe a entrada e faz o armazenamento dos tokens e da gramatica
def pegar_entrada():
    l_tokens = []
    l_gr = []
    flag = True
    a = open('entrada.txt', 'r')
    a = a.readlines()
    for l in a:
        linha = l.strip()
        if linha != '' and flag == True:
            l_tokens.append(linha)
        else:
            flag = False
            if linha != '':
                l_gr.append(linha)
    return l_tokens, l_gr

#Adiciona os tokens em um AFND, juntamente com suas características
def adicionar_tokens(AFND, tokens):
	for i in tokens:
		posicao = 0
		for j in i:
			producao = AFND[posicao]
			if producao != '':
				producao += ' '
			producao += j + '<' + str(len(AFND)) + '>'
			AFND[posicao] = producao
			posicao = len(AFND)
			AFND.append('<' + str(posicao) + '> ::=')
		AFND[len(AFND)-1] += ' eps'
	return AFND

# Adiciona a gramatica ao AFND
def adicionar_gramatica(AFND, gr):
	for i in gr:
		p = ''
		for j in i:
			p += j
			if j == 'S':
				p += '\''
		if i[1] == 'S':
			prod = AFND[0]
			prod += p[8:]
			AFND[0] = prod
		AFND.append(p)
	return AFND

# Retorna todos os simbolos finais em ordem
def get_simbolos_finais(AFND):
	simbolos_finais = []
	for i in AFND:
		for j in i[2:]:
			if j == '|' or j == 'eps':
				continue
			if j[0] not in simbolos_finais:
				simbolos_finais.append(j[0])
	return sorted(simbolos_finais)

# Cria uma lista onde será armazenada n "itens" em branco que servirão para saber qual é o próximo estado
def create_producao(tam_simbolos_finais):
	producao = []
	for i in range(tam_simbolos_finais):
		producao.append('')
	return producao

# Retorna as produções daquele automato
def get_producao(producao, AFND):
	for i in AFND:
		if i[0] == producao:
			return i
	return []

# Preenche a lista criada em create_producao, preenchendo com o próximo estado, caso tenha mais de um estado é utilizado um espaço entre as duas para ajudar na determinização
def get_listas(listas, producao, AFND, simbolos_finais):
	producoes = get_producao(producao, AFND)
	for i in producoes[2:]:
		if i == '|' or i =='eps':
			continue
		index = simbolos_finais.index(i[0])
		if len(i) > 1:
			if i[2:-1] in listas[index]:
				continue
			prod = i[2:-1]
		else:
			if 'X' in listas[index]:
				continue
			prod = 'X'
		if listas[index] != '':
			listas[index] += ' '
		listas[index] += prod
	return listas

# Procura e retorna se aquela produção já se encontra na lista de produções
def checar_producao(producoes, prod, flag):
	i = '<'
	if flag:
		i += '_'
	prod = i + prod + '>'
	return prod in producoes

# Se aquela produção não tiver na lista de produções ele adiciona ela a lista e no fim retorna esse lista com as novas produções
def procurar_nova_producao(lista, fila_novas_producoes, producoes):
	for i in lista:
		if i == '':
			continue
		if ' ' in i:
			flag = True
		else:
			flag = False
		if not checar_producao(producoes, i, flag):
			fila_novas_producoes.insert(0, i)
	return fila_novas_producoes

# Retira os espaços que poderiam existir na identificação do próximo estado
def arrumar_novas_producoes(lista):
	for i in range(len(lista)):
		if ' ' in lista[i]:
			novo_comeco = '_'
			for j in sorted(lista[i]):
				if j == ' ':
					continue
				novo_comeco += j
			lista[i] = novo_comeco
	return lista

# Retirar o espaço daquela determinada produção
def limpar_producao(producao):
	p = ''
	for i in producao:
		if i == ' ':
			continue
		p += i
	return p

def determinizar(AFND):
	simbolos_finais = get_simbolos_finais(AFND)
	fila_producoes = []
	producoes_AFD = []
	AFD = []
	for i in AFND:
		producoes_AFD.append(i[0])
	for i in AFND:
		nome_producao = [i[0]]
		lista_producao = create_producao(len(simbolos_finais))									#Cria uma lista com as "posições" dos próximos estados
		lista_producao = get_listas(lista_producao, i[0], AFND, simbolos_finais)				#Preenche as produções com os próximos estados na lista
		fila_producoes = procurar_nova_producao(lista_producao, fila_producoes, producoes_AFD)	#Procura se tem um novo estado e adiciona elas a fila
		lista_producao = arrumar_novas_producoes(lista_producao)								#Retira os espaços contidos nas "posições" das produções
		i_eps = ['']
		if 'eps' in i:
			i_eps = ['eps']
		AFD.append([nome_producao, lista_producao, i_eps])										#Adiciona os "resultados" no AFD
	while fila_producoes != []:
		nome_p_fila = fila_producoes.pop()
		nome_p_fila_split = nome_p_fila.split()
		nome_p_fila = limpar_producao(sorted(nome_p_fila))
		if checar_producao(producoes_AFD, nome_p_fila, True):									#Verifica se aquele estado já é uma estado se for vai para a próxima iteração
			continue
		nome_p_fila = '<_' + nome_p_fila + '>'
		producoes_AFD.append(nome_p_fila)														#Adiciona a nova regra em estados
		nome_producao = [nome_p_fila]
		lista_producao = create_producao(len(simbolos_finais))									#Cria uma lista com as "posições" dos próximos estados
		i_eps = ['']
		for i in nome_p_fila_split:
			p_i = get_producao('<' + i + '>', AFND)												#Adiciona as producões ao p_i
			if 'eps' in p_i:																	#Confere se tiver eps nas produções ele adiciona um eps naquele estado
				i_eps = ['eps']
			lista_producao = get_listas(lista_producao, '<' + i + '>', AFND, simbolos_finais)	#Preenche as produções com o próximo estado
		fila_producoes = procurar_nova_producao(lista_producao, fila_producoes, producoes_AFD)	#Procura se tem uma nova produção e adiciona elas a fila
		lista_producao = arrumar_novas_producoes(lista_producao)								#Retira os espaços contidos nas "posições" dos próximos estados
		AFD.append([nome_producao, lista_producao, i_eps])										#Adiciona em AFD
	tam = 0
	for i in AFD:
		for j in i[0]:
			if j == '<_X>':
				AFD[tam][0] = ['<X>']
				AFD[tam][2] = 'eps'
			tam += 1
	return AFD

def minimizacao():
	pegarAlcancaveis(AFD, alcancaveis, 0)
	eliminarInalcancaveis(AFD, alcancaveis)

# Percorre o automato recursivamente em busca daqueles que são alcançáveis
def pegarAlcancaveis(AFD, alcancaveis, indice):
	index = alcancaveis[indice]
	for i in AFD:
		if index in i[0]:
			for j in i[1]:
				aux = '<' + j + '>'
				if j != '' and aux not in alcancaveis:
					alcancaveis.append('<' + j + '>')
	if len(alcancaveis) > indice+1:
		pegarAlcancaveis(AFD, alcancaveis, indice+1)

# Elimina os inalcançáveis de trás para frente
def eliminarInalcancaveis(AFD, alcancaveis):
	for i in range(len(AFD)-1, 0, -1):
		if AFD[i][0][0] not in alcancaveis:
			AFD.remove(AFD[i])

def exibir(AFD, AFND):
	simbolos_finais = get_simbolos_finais(AFND)
	print(simbolos_finais)

	for i in AFD:
		frase = ''
		frase += i[0][0] + ' ::= '
		prox = []
		for j in i[1]:
			if j == '':
				j = '-'
			prox.append('<' + j + '>')
		for j in range(len(prox)):
			if j != 0:
				frase += ' | '
			frase += simbolos_finais[j] + prox[j]
		if i[2][0] != '':
			frase += ' | eps'
		#print(frase)

# Ler arquivo fonte
def analisadorLexico(AFD, AFND, listaIndicesEstados, tokensList):
	arq = open("fonte.txt", "r")
	arq = arq.readlines()
	listaTS = []
	listaVariaveis = []
	for numLinha, linha in enumerate(arq):
		linhaSplitted = linha.strip().split(" ")
		for token in linhaSplitted:
			estado = reconhecerEstado(token, AFD, AFND, listaIndicesEstados)
			if token in tokensList:
				tipo = token
				id = None
			else:
				try:
					float(token)
					tipo = "num"
					id = None
				except:
					tipo = "id"
					if token not in listaVariaveis:
						listaVariaveis.append(token)
						id = listaVariaveis.index(token)
					else:
						id = listaVariaveis.index(token)
			listaTS.append(ObjectoTS(numLinha, token, tipo, estado, None, id))
	listaTS.append(ObjectoTS(numLinha, "EOF", "EOF", "EOF", "EOF", "EOF"))
	for i in listaTS:
		if i.estado == "erro":
			print("Erro léxico na linha {} com token: '{}' ".format(i.linha, i.rotulo))
			return False, listaTS
	return True, listaTS
		

def indexEstados(AFD):
	listEstados = {}
	for j,i in enumerate(AFD):
		listEstados[i[0][0]] = j
	return listEstados

def reconhecerEstado(token, AFD, AFND, listaIndicesEstados):
	simbolosFinais = get_simbolos_finais(AFND)
	estado = 0
	indexLetra = 0
	indice = 0
	for letra in token:
		if letra not in simbolosFinais:
			return "erro"
		else:
			indexLetra = simbolosFinais.index(letra)
			prox = AFD[estado][1][indexLetra]
			if prox == '':
				return "erro"
			indice = listaIndicesEstados['<'+prox+'>']
			estado = indice
	return indice

def lerXML():
	xml = ET.parse('LALRTable.xml')
	raiz = xml.getroot()

	simbolos = raiz.iter('m_Symbol')
	producoes = raiz.iter('m_Production')
	tabelaLALR = raiz.iter('LALRTable')

	# Mapeando resultados
	simbolosMap = {}
	for s in simbolos:
		for i in s:
			simbolosMap[i.attrib["Name"]] = i.attrib["Index"]

	producoesMap = []
	for p in producoes:
		for i in p:
			a = (i.attrib["NonTerminalIndex"], i.attrib["SymbolCount"])
			producoesMap.append(a)
	
	lalrMap = []
	for t in tabelaLALR:
		for i in t:
			lEstados = []
			for j in i:
				a = (j.attrib["SymbolIndex"], j.attrib["Action"], j.attrib["Value"])
				lEstados.append(a)
			lalrMap.append(lEstados)

	return simbolosMap, producoesMap, lalrMap

def analisadorSintatico(listaTS, simbolosMap, producoesMap, lalrMap):
	estadoAtualFita = 0

	pilha = []
	pilha.append('0')

	fita = []
	fitaLinha = []
	for s in listaTS:
		fita.append(s.tipo)
		fitaLinha.append(s.linha)

	'''Convertendo fita para seus respectivos índices, exemplo: int tem como seu índice 20,
	# agora com a conversão temos no lugar de int o 20.'''
	for i,j in enumerate(fita):
		fita[i] = simbolosMap[j]

	#print(lalrMap)
	#print(producoesMap)

	status = ''
	while(status != 'AC'):
		estadoTabela = lalrMap[int(pilha[-1])]
		encontrado = False
		for simb in estadoTabela:
			if simb[0] == fita[estadoAtualFita]:
				acao, valor = simb[1], simb[2]
				simbE = simb[0]
				encontrado = True 
				break
		if encontrado:
			if acao == '1':
				pilha.append(simbE)
				pilha.append(valor)
				estadoAtualFita += 1
			elif acao == '2':
				#retirar dobro
				tupla = producoesMap[int(valor)] # NomeDaRegra, Tamanho
				desempilha = len(pilha) - 2 * int(tupla[1])
				del pilha[desempilha:]
				#empilha nome regra
				pilha.append(tupla[0])
				#verifica salto
				proxEstado = lalrMap[int(pilha[-2])]
				encontrado2 = False
				for i in proxEstado:
					if i[0] == pilha[-1]: 
						acao, valor = i[1],i[2]
						if acao == '3':
							pilha.append(valor)
						encontrado2 = True
						break
				if not encontrado2:
					print('Erro sintático na linha {}'.format(fitaLinha[estadoAtualFita]))
					break
			elif acao == '3':
				pilha.append(valor)
			elif acao == '4':
				print('Aceita')
				status = 'AC'
		else:
			print('Erro sintático na linha {}'.format(fitaLinha[estadoAtualFita]))
			break


tokens, gr = pegar_entrada()
AFND = []
AFND.append('<S> ::=')
AFND = adicionar_tokens(AFND, tokens)
AFND = adicionar_gramatica(AFND, gr)
for i in range(len(AFND)):
    AFND[i] = AFND[i].split()
AFD = determinizar(AFND)
alcancaveis = ['<S>']
minimizacao()
eliminarInalcancaveis(AFD, alcancaveis)
#print(AFD,type(AFD),len(AFD))
exibir(AFD, AFND)
listaIndicesEstados = indexEstados(AFD)
statusAL, listaTS = analisadorLexico(AFD, AFND, listaIndicesEstados, tokens)
if statusAL:
	'''print("TABELA DE SÍMBOLOS")
	for i in listaTS:
		print(i.linha, i.rotulo, i.tipo, i.estado, i.tipoVar, i.id)'''
	simbolosMap, producoesMap, lalrMap = lerXML()
	analisadorSintatico(listaTS, simbolosMap, producoesMap, lalrMap)