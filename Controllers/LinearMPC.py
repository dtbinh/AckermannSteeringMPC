import numpy as np
import cvxopt

cvxopt.matrix_repr = cvxopt.printing.matrix_str_default
cvxopt.printing.options['dformat'] = '%.2f'
cvxopt.printing.options['width'] = -1
cvxopt.solvers.options['show_progress'] = True

def getControl(A, B, C, x, r, g, h, stateLength, controlLength, N, Q, R, S, Cbar):

	A=cvxopt.matrix(A)
	B=cvxopt.matrix(B)
	C=cvxopt.matrix(C)

	x=cvxopt.matrix(x)
	r=cvxopt.matrix(r)

	if(not (g==None or h==None)):
		g=cvxopt.matrix(g)
		h=cvxopt.matrix(h)

	Q=cvxopt.matrix(Q)
	R=cvxopt.matrix(R)
	S=cvxopt.matrix(S)
	
	Cbar=cvxopt.matrix(Cbar)

	Atilde=A
	Btilde=B
	Ctilde=C

	Rhat=cvxopt.spdiag([R for i in range(0,N)])
	Qhat=cvxopt.spdiag([Ctilde.trans()*Q*Ctilde if i<(N-1) else Ctilde.trans()*S*Ctilde for i in range(0,N)])

	b=[]
	temp=cvxopt.matrix(np.eye(stateLength))
	for i in range(0,N):
		b.append(temp)
		temp=temp+Atilde*b[-1]

	T1=cvxopt.sparse(b)
	Chat=T1*Cbar

	b=[]
	for i in range(0,N):
		a=[]
		if(i!=N-1):
			temp=Q*Ctilde
		else:
			temp=S*Ctilde
		for j in range(0,N):
			if(j==i):
				a.append(temp)
			else:
				a.append(cvxopt.matrix(np.zeros((stateLength, stateLength))).trans())
		b.append(a)

	That=cvxopt.sparse(b)
	

	b=[]
	for i in range(0,N):
		a=[]
		for j in range(0,N):
			if(j<=i):
				a.append((cvxopt.matrix(np.linalg.matrix_power(Atilde, N-1-j))*Btilde).trans())
			else:
				a.append(cvxopt.matrix(np.zeros(Btilde.size)).trans())
		b.append(a)

	Bhat=cvxopt.sparse(b).trans()
	Ahat=cvxopt.sparse([cvxopt.matrix(np.linalg.matrix_power(Atilde, i+1)) for i in range(0,N)])

	#Final Matrices
	P1=(Bhat.trans()*Qhat*Bhat+Rhat)/2
	xAdj=cvxopt.sparse([x, r, Chat])
	F=cvxopt.sparse([[Bhat.trans()*Qhat.trans()*Ahat],[-Bhat.trans()*That.trans()], [Bhat.trans()*Qhat.trans()]])
	q=cvxopt.matrix(F*xAdj)
	#print(q)

	if(not (g==None or h==None)):
		G=g
		H=h
	else:
		G=None
		H=None

	sol=cvxopt.solvers.qp(P1,q,G,H)
	print(sol)

	return sol['x'][0:controlLength]

