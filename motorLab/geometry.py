"""Geometria plana genérica; sem modelos físicos ou integração de simulação."""
from copy import deepcopy
from math import isfinite

LIMIT = 1000000


def number(value, minimum=-LIMIT, maximum=LIMIT):
    return type(value) in (int, float) and isfinite(value) and minimum <= value <= maximum


def validate_points(points):
    if not isinstance(points, list) or not 3 <= len(points) <= 200:
        raise ValueError("O polígono deve ter de 3 a 200 vértices.")
    if any(not isinstance(p, list) or len(p) != 2 or not all(number(v) for v in p) for p in points):
        raise ValueError("Vértices inválidos: use coordenadas numéricas finitas.")
    def cross(a, b, c):
        return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def on(a, b, p):
        return min(a[0],b[0]) <= p[0] <= max(a[0],b[0]) and min(a[1],b[1]) <= p[1] <= max(a[1],b[1])
    n = len(points)
    for i in range(n):
        a, b = points[i], points[(i+1)%n]
        if a == b:
            raise ValueError("Existem vértices consecutivos repetidos.")
        for j in range(i+1,n):
            if j == i+1 or (i == 0 and j == n-1):
                continue
            c, d = points[j], points[(j+1)%n]
            x, y, z, w = cross(a,b,c), cross(a,b,d), cross(c,d,a), cross(c,d,b)
            if (x*y < 0 and z*w < 0) or any((v == 0 and on(p,q,r)) for v,p,q,r in ((x,a,b,c),(y,a,b,d),(z,c,d,a),(w,c,d,b))):
                raise ValueError("As arestas do polígono não podem se cruzar ou se tocar.")
    area2 = sum(points[i][0]*points[(i+1)%n][1]-points[(i+1)%n][0]*points[i][1] for i in range(n))
    if abs(area2) < 1e-8:
        raise ValueError("O polígono precisa ter área diferente de zero.")


def validate_geometry(geometry):
    if not isinstance(geometry, dict) or set(geometry) != {"units", "shapes"} or geometry["units"] != "mm":
        raise ValueError("Geometria inválida; a unidade deve ser mm.")
    shapes = geometry["shapes"]
    if not isinstance(shapes, list) or len(shapes) > 500:
        raise ValueError("O desenho deve conter até 500 formas.")
    ids = set()
    for s in shapes:
        if not isinstance(s, dict) or s.get("type") not in ("circle", "polygon"):
            raise ValueError("Tipo de forma inválido.")
        extra = "radius" if s["type"] == "circle" else "points"
        if set(s) != {"id", "name", "type", "x", "y", extra}:
            raise ValueError("Estrutura de forma inválida.")
        if not isinstance(s["id"], str) or not s["id"] or s["id"] in ids:
            raise ValueError("Identificador de forma vazio ou repetido.")
        ids.add(s["id"])
        if not isinstance(s["name"], str) or not number(s["x"]) or not number(s["y"]):
            raise ValueError("Nome ou posição da forma inválidos.")
        if s["type"] == "circle":
            if not number(s["radius"], .0005, LIMIT/2):
                raise ValueError("Diâmetro fora dos limites do editor.")
        else:
            validate_points(s["points"])
    return deepcopy(geometry)
