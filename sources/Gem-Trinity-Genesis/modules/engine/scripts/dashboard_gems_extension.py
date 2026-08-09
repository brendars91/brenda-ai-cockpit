"""
Actualización del Dashboard de AGCCE para mostrar Gems activos

Este script extiende el dashboard existente añadiendo una sección
para visualizar Gem Bundles registrados y su estado de uso.
"""
import json
from pathlib import Path


def generate_gems_dashboard_section() -> str:
    """
    Genera HTML para la sección de Gems del dashboard.
    
    Returns:
        HTML string con la sección de Gems
    """
    # Cargar registry
    registry_path = Path("config/gem_registry.json")
    
    if not registry_path.exists():
        return """
        <div class="card">
            <h3>🔷 Gem Bundles</h3>
            <p style="color: #888;">No hay Gems registrados aún.</p>
            <p><small>Los Gem Bundles aparecerán aquí cuando uses GemPlans.</small></p>
        </div>
        """
    
    with open(registry_path) as f:
        registry = json.load(f)
    
    gems = []
    for use_case_id, gem_data in registry.get('gems', {}).items():
        for version, version_data in gem_data['versions'].items():
            gems.append({
                "use_case_id": use_case_id,
                "version": version,
                "is_latest": version == gem_data['latest_version'],
                **version_data
            })
    
    if not gems:
        return generate_gems_dashboard_section.__doc__.split('Returns:')[1]  # Fallback
    
    # Ordenar por uso
    gems.sort(key=lambda x: x.get('usage_count', 0), reverse=True)
    
    # Generar tabla HTML
    rows = ""
    for gem in gems[:10]:  # Top 10
        latest_badge = '<span style="background: #4CAF50; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em;">LATEST</span>' if gem['is_latest'] else ''
        
        risk_color = '#f44336' if gem['risk_score'] > 60 else ('#FF9800' if gem['risk_score'] > 30 else '#4CAF50')
        
        rows += f"""
        <tr>
            <td><strong>{gem['use_case_id']}</strong> {latest_badge}</td>
            <td>v{gem['version']}</td>
            <td>{gem['model']}</td>
            <td><span style="color: {risk_color}; font-weight: bold;">{gem['risk_score']}</span></td>
            <td>{gem.get('usage_count', 0)}</td>
            <td style="font-size: 0.9em; color: #888;">{gem.get('last_used', 'Nunca')[:10] if gem.get('last_used') else 'N/A'}</td>
        </tr>
        """
    
    stats = {
        "total": len(gems),
        "cached_profiles": len(registry.get('profiles_cache', {}))
    }
    
    return f"""
    <div class="card">
        <h3>🔷 Gem Bundles Registrados</h3>
        <p><strong>Total:</strong> {stats['total']} Gems | <strong>Profiles Cacheados:</strong> {stats['cached_profiles']}</p>
        
        <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
            <thead>
                <tr style="background: #f5f5f5; text-align: left;">
                    <th style="padding: 8px;">Use Case</th>
                    <th style="padding: 8px;">Versión</th>
                    <th style="padding: 8px;">Modelo</th>
                    <th style="padding: 8px;">Risk</th>
                    <th style="padding: 8px;">Usos</th>
                    <th style="padding: 8px;">Último Uso</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>
        
        <p style="margin-top: 15px; font-size: 0.9em; color: #666;">
            Mostrando top {min(10, len(gems))} Gems por uso.
        </p>
    </div>
    """


# Snippet para insertar en dashboard/index.html
DASHBOARD_INSERT_SNIPPET = """
<!-- GEM BUNDLES SECTION - Insertar después de la sección de métricas -->
<script>
// Cargar sección de Gems dinámicamente
fetch('/api/gems')
    .then(res => res.json())
    .then(data => {
        const container = document.getElementById('gems-section');
        if (container) {
            container.innerHTML = renderGemsSection(data);
        }
    });

function renderGemsSection(registry) {
    const gems = [];
    for (const [useCase, data] of Object.entries(registry.gems || {})) {
        for (const [version, versionData] of Object.entries(data.versions || {})) {
            gems.push({
                useCase,
                version,
                isLatest: version === data.latest_version,
                ...versionData
            });
        }
    }
    
    if (gems.length === 0) {
        return `
            <div class="card">
                <h3>🔷 Gem Bundles</h3>
                <p style="color: #888;">No hay Gems registrados aún.</p>
            </div>
        `;
    }
    
    gems.sort((a, b) => (b.usage_count || 0) - (a.usage_count || 0));
    
    let rows = gems.slice(0, 10).map(gem => {
        const latestBadge = gem.isLatest ? '<span class="badge">LATEST</span>' : '';
        const riskColor = gem.risk_score > 60 ? '#f44336' : (gem.risk_score > 30 ? '#FF9800' : '#4CAF50');
        
        return `
            <tr>
                <td><strong>${gem.useCase}</strong> ${latestBadge}</td>
                <td>v${gem.version}</td>
                <td>${gem.model}</td>
                <td><span style="color: ${riskColor}; font-weight: bold;">${gem.risk_score}</span></td>
                <td>${gem.usage_count || 0}</td>
                <td>${gem.last_used ? gem.last_used.substring(0, 10) : 'N/A'}</td>
            </tr>
        `;
    }).join('');
    
    return `
        <div class="card">
            <h3>🔷 Gem Bundles Registrados</h3>
            <p><strong>Total:</strong> ${gems.length} Gems | <strong>Profiles Cacheados:</strong> ${Object.keys(registry.profiles_cache || {}).length}</p>
            
            <table class="gems-table">
                <thead>
                    <tr>
                        <th>Use Case</th>
                        <th>Versión</th>
                        <th>Modelo</th>
                        <th>Risk</th>
                        <th>Usos</th>
                        <th>Último Uso</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        </div>
    `;
}
</script>

<style>
.gems-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
}

.gems-table thead tr {
    background: #f5f5f5;
    text-align: left;
}

.gems-table th, .gems-table td {
    padding: 8px;
    border-bottom: 1px solid #ddd;
}

.badge {
    background: #4CAF50;
    color: white;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 0.8em;
    margin-left: 5px;
}
</style>

<!-- Contenedor para la sección de Gems -->
<div id="gems-section"></div>
"""

if __name__ == "__main__":
    # Generar sección de Gems
    html = generate_gems_dashboard_section()
    print(html)
