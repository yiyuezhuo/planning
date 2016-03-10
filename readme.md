# Planning

## Example

### Problem

In `plane_problem.txt` ,it include a problem description by STRIPS.

		Init(At(C1,SFO) & At(C2,JFK) & At(P1,SFO) 
			& At(P2,JFK) & Cargo(C1) & Cargo(C2) & Plane(P1)
			& Plane(P2) & Airport(JFK) & Airport(SFO))

		Goal(At(C1,JFK) & At(C2,SFO))

		Action(Load(c,p,a),
			PRECOND:At(c,a) & At(p,a) & Cargo(c) & Plane(p) & Airport(a)
			EFFECT:~At(c,a) & In(c,p))

		Action(Unload(c,p,a),
			PRECOND:In(c,p) & At(p,a) & Cargo(c) & Plane(p) & Airport(a)
			EFFECT: At(c,a) & ~In(c,p))

		Action(Fly(p,from,to),
			PRECOND:At(p,from) & Plane(p) & Airport(from) & Airport(to)
			EFFECT:~At(p,from) & At(p,to))
	
To solve it:

		In [1]: runfile('E:/agent4/planning/core.py', wdir='E:/agent4/planning')

		In [2]: pp=load('plane_problem.txt')

		In [3]: solve(pp)
		Load(C1,P1,SFO)
		Load(C2,P2,JFK)
		Fly(P1,SFO,JFK)
		Fly(P2,JFK,SFO)
		Unload(C1,P1,JFK)
		Unload(C2,P2,SFO)

However,it use general breadth-first search to solve so it's slow.