# Guía de Contribución — nexus_organizer

## Estructura de ramas

| Rama | Propósito | Base |
|------|-----------|------|
| `main` | Código en producción, protegida | — |
| `develop` | Integración de desarrollo activo | `main` |
| `feature/<nombre>` | Nueva funcionalidad | `develop` |
| `fix/<nombre>` | Corrección de bugs | `develop` |
| `release/<version>` | Preparación de release | `develop` |
| `hotfix/<nombre>` | Fix crítico en producción | `main` |

## Flujo de trabajo

```bash
# 1. Crear rama desde develop
git checkout develop
git pull origin develop
git checkout -b feature/mi-nueva-funcionalidad

# 2. Desarrollar y hacer commits
git add <archivos>
git commit -m "feat(scope): descripción concisa"

# 3. Push y abrir PR hacia develop
git push origin feature/mi-nueva-funcionalidad
```

## Convención de commits (Conventional Commits)

```
<tipo>(<scope>): <descripción corta>

[cuerpo opcional]

[footer opcional: Closes #NNN]
```

### Tipos permitidos

| Tipo | Uso |
|------|-----|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de bug |
| `docs` | Solo documentación |
| `refactor` | Refactorización sin cambio funcional |
| `style` | Formato, espacios (sin cambio lógico) |
| `test` | Tests |
| `chore` | Build, dependencias, tareas de mantenimiento |
| `ci` | Cambios en pipelines CI/CD |

### Ejemplos

```
feat(organizer): añadir soporte para archivos .mkv
fix(config): corregir lectura de rutas con espacios
docs(readme): actualizar instrucciones de instalación
chore(deps): actualizar watchdog a 3.0.0
```

## Reglas importantes

- **Nunca** hacer push directo a `main`
- **Siempre** abrir PR para mergear a `main` o `develop`
- **Nunca** subir credenciales, tokens, contraseñas ni rutas absolutas personales
- Archivos `.env`, `*.log`, `*_history.json` están en `.gitignore` — respetar esa lista
- Los commits deben ser atómicos: un cambio lógico por commit

## Versionado

Se sigue [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- `MAJOR` — cambios incompatibles con versiones anteriores
- `MINOR` — nueva funcionalidad compatible
- `PATCH` — corrección de bugs compatible
