export class ApiConfig {
  // URL base del servidor
  private static readonly BASE_URL = 'http://localhost:8000/api';
  
  // URLs específicas por módulo
  public static readonly ENDPOINTS = {
    USUARIOS: `${ApiConfig.BASE_URL}/usuarios`,
    CURSOS: `${ApiConfig.BASE_URL}/cursos`,
    BASE: ApiConfig.BASE_URL
  };

  // Método para cambiar la URL base (útil para diferentes entornos)
  public static setBaseUrl(newBaseUrl: string): void {
    // Actualizar dinámicamente las URLs
    Object.keys(ApiConfig.ENDPOINTS).forEach(key => {
      if (key === 'USUARIOS') {
        (ApiConfig.ENDPOINTS as any)[key] = `${newBaseUrl}/usuarios`;
      } else if (key === 'CURSOS') {
        (ApiConfig.ENDPOINTS as any)[key] = `${newBaseUrl}/cursos`;
      } else if (key === 'BASE') {
        (ApiConfig.ENDPOINTS as any)[key] = newBaseUrl;
      }
    });
  }

  // Método para obtener URL completa de un endpoint
  public static getUrl(endpoint: string): string {
    return `${ApiConfig.BASE_URL}${endpoint}`;
  }
}