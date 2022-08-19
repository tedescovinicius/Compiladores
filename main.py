from ObjetoTS import *
import xml.etree.ElementTree as ET

def getExibicao(AFD, AFND):
	finaisSimbolos = pegaSimbolosFinais(AFND)
	print(finaisSimbolos)

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
			frase += finaisSimbolos[j] + prox[j]
		if i[2][0] != '':
			frase += ' | eps'
		#print(frase)

#
# Função responsável pela adição do AFNF na grámtica 
#
def incluir_gramatica(AFND, gramatica):
	for i in gramatica:
		h = ''
		for j in i:
			h += j
			if j == 'S':
				h += '\''
		if i[1] == 'S':
			prod = AFND[0]
			prod += h[8:]
			AFND[0] = prod
		AFND.append(h)
	return AFND

#
# Função onde adiciona os tokens em um AFND, de ceta maneira juntamento com suas características
#
def tokens_inclusao(AFND, tokens):
	for i in tokens:
		posicaoToken = 0
		for j in i:
			prodAFND = AFND[posicaoToken]
			if prodAFND != '':
				prodAFND += ' '
			prodAFND += j + '<' + str(len(AFND)) + '>'
			AFND[posicaoToken] = prodAFND
			posicaoToken = len(AFND)
			AFND.append('<' + str(posicaoToken) + '> ::=')
		AFND[len(AFND)-1] += ' eps'
	return AFND

##
# Função responsáveç por retorna todos os simbolos finais em ordem
##
def pegaSimbolosFinais(AFND):
	##pega simbolos finais em ordem AFN
	simbolos_finais = []
	for i in AFND:
		for j in i[2:]:
			if j == '|' or j == 'eps':
				continue
			if j[0] not in simbolos_finais:
				simbolos_finais.append(j[0])
	return sorted(simbolos_finais)

##
# Função capaz de criar uma lista onde será armazenada n "itens" em branco que servirão para saber qual é o próximo estado
##
def criarNovaProducao(tamanhoSimbolosFinais):
	producao = []
	for i in range(tamanhoSimbolosFinais):
		producao.append('')
	return producao
##
# Funão onde recebe a entrada e faz o armazenamento dos tokens e da gramatica
##
def incluir_obj_entrada():
    inclu_tokens = []
    inclu_gram = []
    flagOperation = True
    arq = open('entrada.txt', 'r')
    arq = arq.readlines()
    for l in arq:
        linha = l.strip()
        if linha != '' and flagOperation == True:
            inclu_tokens.append(linha)
        else:
            flagOperation = False
            if linha != '':
                inclu_gram.append(linha)
    return inclu_tokens, inclu_gram
##
# Função capar de retorna as produções pertencente ao automato
##
def buscaProducao(producao, AFND):
	for i in AFND:
		if i[0] == producao:
			return i
	return []

##
# Preenche a lista criada em criarNovaProducao, preenchendo com o próximo estado, 
# caso tenha mais de um estado é utilizado um espaço entre as duas para ajudar na determinização
##
def buscaListasProd(listas, producao, AFND, finaisSimbolos):
	producoes = buscaProducao(producao, AFND)
	for i in producoes[2:]:
		if i == '|' or i =='eps':
			continue
		index = finaisSimbolos.index(i[0])
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

##
# Procura e retorna se aquela produção já se encontra na lista de produções
##
def validaProducao(producoes, prod, flagOperation):
	i = '<'
	if flagOperation:
		i += '_'
	prod = i + prod + '>'
	return prod in producoes
##
# Se aquela produção não tiver na lista de produções ele adiciona ela a 
# lista e no fim retorna esse lista com as novas produções
##
def novaProducaoProcurar(lista, fila_novas_producoes, producoes):
	for i in lista:
		if i == '':
			continue
		if ' ' in i:
			flagOperation = True
		else:
			flagOperation = False
		if not validaProducao(producoes, i, flagOperation):
			fila_novas_producoes.insert(0, i)
	return fila_novas_producoes

##
# Função responsável por Retirar o espaço daquela determinada produção
##
def corrigirLimparProducao(producao):
	p = ''
	for i in producao:
		if i == ' ':
			continue
		p += i
	return p

##
# Função responsável por retira os espaços que poderiam existir na identificação do próximo estado
##
def corrigirNovasProducoes(lista):
	for i in range(len(lista)):
		if ' ' in lista[i]:
			novo_comeco = '_'
			for j in sorted(lista[i]):
				if j == ' ':
					continue
				novo_comeco += j
			lista[i] = novo_comeco
	return lista

##
##Funcões abaixo responsávl pela minimização e determinização do AFND
##
def minimizacaoAFND():
	getAlcancaveis(AFD, alcancaveis, 0)
	deleteInalcancaveis(AFD, alcancaveis)


##
# Função responsável por fazer a derminzação do AFND
##
def determinizacaoAFND(AFND):
	finaisSimbolos = pegaSimbolosFinais(AFND)
	fila_producoes = []
	producoes_AFD = []
	AFD = []
	for i in AFND:
		producoes_AFD.append(i[0])
	for i in AFND:
		nome_producao = [i[0]]
		#Cria uma lista com as "posições" dos próximos estados
		lista_producao = criarNovaProducao(len(finaisSimbolos))
		#Preenche as produções com os próximos estados na lista									
		lista_producao = buscaListasProd(lista_producao, i[0], AFND, finaisSimbolos)
		#Procura se tem um novo estado e adiciona elas a fila				
		fila_producoes = novaProducaoProcurar(lista_producao, fila_producoes, producoes_AFD)	
		#Retira os espaços contidos nas "posições" das produções
		lista_producao = corrigirNovasProducoes(lista_producao)								
		i_eps = ['']
		if 'eps' in i:
			i_eps = ['eps']
		#Adiciona os "resultados" no AFD	
		AFD.append([nome_producao, lista_producao, i_eps])										
	while fila_producoes != []:
		nome_p_fila = fila_producoes.pop()
		nome_p_fila_split = nome_p_fila.split()
		nome_p_fila = corrigirLimparProducao(sorted(nome_p_fila))
		#Verifica se aquele estado já é uma estado se for vai para a próxima iteração
		if validaProducao(producoes_AFD, nome_p_fila, True):									
			continue
		nome_p_fila = '<_' + nome_p_fila + '>'
		#Adiciona a nova regra em estados
		producoes_AFD.append(nome_p_fila)														
		nome_producao = [nome_p_fila]
		#Cria uma lista com as "posições" dos próximos estados
		lista_producao = criarNovaProducao(len(finaisSimbolos))									
		i_eps = ['']
		for i in nome_p_fila_split:
			#Adiciona as producões ao p_i
			p_i = buscaProducao('<' + i + '>', AFND)
			#Confere se tiver eps nas produções ele adiciona um eps naquele estado												
			if 'eps' in p_i:																	
				i_eps = ['eps']
			#Preenche as produções com o próximo estado
			lista_producao = buscaListasProd(lista_producao, '<' + i + '>', AFND, finaisSimbolos)
		#Procura se tem uma nova produção e adiciona elas a fila	
		fila_producoes = novaProducaoProcurar(lista_producao, fila_producoes, producoes_AFD)
		#Retira os espaços contidos nas "posições" dos próximos estados	
		lista_producao = corrigirNovasProducoes(lista_producao)
		#Adiciona em AFD								
		AFD.append([nome_producao, lista_producao, i_eps])										
	tam = 0
	for i in AFD:
		for j in i[0]:
			if j == '<_X>':
				AFD[tam][0] = ['<X>']
				AFD[tam][2] = 'eps'
			tam += 1
	return AFD

##
# Funcão resposável por eliminar os inalcançáveis de trás para frente
##
def deleteInalcancaveis(AFD, alcancaveis):
	for i in range(len(AFD)-1, 0, -1):
		if AFD[i][0][0] not in alcancaveis:
			AFD.remove(AFD[i])

##
# Funcão responsável por percorrer o automato recursivamente em busca daqueles que são alcançáveis
##
def getAlcancaveis(AFD, alcancaveis, indice):
	index = alcancaveis[indice]
	for i in AFD:
		if index in i[0]:
			for j in i[1]:
				aux = '<' + j + '>'
				if j != '' and aux not in alcancaveis:
					alcancaveis.append('<' + j + '>')
	if len(alcancaveis) > indice+1:
		getAlcancaveis(AFD, alcancaveis, indice+1)

##
# Função resposável por pegar o estados do AFD
##
def getIndexEstados(AFD):
	listEstados = {}
	for j,i in enumerate(AFD):
		listEstados[i[0][0]] = j
	return listEstados

##
# Funcão para obter o analisador lexico
##
def functionObterAnalisadorLexico(AFD, AFND, listaIndicesEstados, tokensList):
	#Abertura do arquivo fonte
	arq = open("fonte.txt", "r") 
	arq = arq.readlines()
	listaTS = []
	listaVariaveis = []
	for numLinha, linha in enumerate(arq):
		linhaSplitted = linha.strip().split(" ")
		for token in linhaSplitted:
			estado = functionReconhecerEstado(token, AFD, AFND, listaIndicesEstados)
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
			print("Ops! Erro léxico ocorrido na linha {} com token: '{}' ".format(i.linha, i.rotulo))
			return False, listaTS
	return True, listaTS
		
##
# Função responsável para reconhecer os estados
##
def functionReconhecerEstado(token, AFD, AFND, listaIndicesEstados):
	simbolosFinais = pegaSimbolosFinais(AFND)
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

##
# Funcão reponsável para fazer a leitura do xml
##
def functionLeituraXML():
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
##
# Funcão responsável pela analisador sintatico
##
def functionAnalisadorSintatico(listaTS, simbolosMap, producoesMap, lalrMap):
	estadoAtualFita = 0

	pilha = []
	pilha.append('0')

	fita = []
	fitaLinha = []
	for s in listaTS:
		fita.append(s.tipo)
		fitaLinha.append(s.linha)

	#Convertendo fita para seus respectivos índices, exemplo: int tem como seu índice 20,
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
				#As tuplas são imutáveis. Tuplas são representadas por uma
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
					print('Ops! Erro sintático ocorrido na linha {}'.format(fitaLinha[estadoAtualFita]))
					break
			elif acao == '3':
				pilha.append(valor)
			elif acao == '4':
				print('Aceite')
				status = 'AC'
		else:
			print('Ops ! Erro sintático ocorrido na linha {}'.format(fitaLinha[estadoAtualFita]))
			break


tokens, gr = incluir_obj_entrada()
AFND = []
AFND.append('<S> ::=')
AFND = tokens_inclusao(AFND, tokens)
AFND = incluir_gramatica(AFND, gr)
for i in range(len(AFND)):
    AFND[i] = AFND[i].split()
AFD = determinizacaoAFND(AFND)
alcancaveis = ['<S>']
minimizacaoAFND()
deleteInalcancaveis(AFD, alcancaveis)
#print(AFD,type(AFD),len(AFD))
getExibicao(AFD, AFND)
listaIndicesEstados = getIndexEstados(AFD)
statusAL, listaTS = functionObterAnalisadorLexico(AFD, AFND, listaIndicesEstados, tokens)
if statusAL:
	print("TABLE SIMBOL")
	for i in listaTS:
		print(i.linha, i.rotulo, i.tipo, i.estado, i.tipoVar, i.id)
	simbolosMap, producoesMap, lalrMap = functionLeituraXML()
	functionAnalisadorSintatico(listaTS, simbolosMap, producoesMap, lalrMap)