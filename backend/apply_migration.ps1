# Script para aplicar la migración de league_members
# Uso: .\apply_migration.ps1 -DBName "nfl_fantasy_db" -Username "tu_usuario" -Password "tu_password"

param(
    [string]$DBName = "nfl_fantasy_db",
    [string]$Username = "postgres",
    [string]$Password = "",
    [string]$Host = "localhost",
    [string]$Port = "5432"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Aplicando migración: league_members" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$migrationFile = Join-Path $PSScriptRoot "database\migrations\002_create_league_members_table.sql"

if (-not (Test-Path $migrationFile)) {
    Write-Host "❌ Error: No se encontró el archivo de migración" -ForegroundColor Red
    Write-Host "   Ruta esperada: $migrationFile" -ForegroundColor Yellow
    exit 1
}

Write-Host "📄 Archivo de migración: $migrationFile" -ForegroundColor Green
Write-Host "🗄️  Base de datos: $DBName" -ForegroundColor Green
Write-Host "👤 Usuario: $Username" -ForegroundColor Green
Write-Host ""

# Solicitar contraseña si no se proporcionó
if ([string]::IsNullOrEmpty($Password)) {
    $securePassword = Read-Host "Ingresa la contraseña de PostgreSQL" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
    $Password = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
}

Write-Host "⏳ Aplicando migración..." -ForegroundColor Yellow

# Configurar variable de entorno para la contraseña
$env:PGPASSWORD = $Password

try {
    # Ejecutar el script SQL
    $output = psql -h $Host -p $Port -U $Username -d $DBName -f $migrationFile 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Migración aplicada exitosamente!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Tablas creadas:" -ForegroundColor Cyan
        Write-Host "  • league_members" -ForegroundColor White
        Write-Host ""
        Write-Host "Próximo paso: Reinicia el servidor backend si está corriendo" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "❌ Error al aplicar la migración:" -ForegroundColor Red
        Write-Host $output -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "❌ Error inesperado:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
} finally {
    # Limpiar la variable de entorno
    Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "Para verificar la tabla creada, ejecuta:" -ForegroundColor Cyan
Write-Host "  psql -h $Host -U $Username -d $DBName -c ""\d league_members""" -ForegroundColor White
Write-Host ""
