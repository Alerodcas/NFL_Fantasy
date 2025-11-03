export const PASSWORD_RE = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z0-9]{8,12}$/;

export function isValidPassword(pw: string): boolean {
  return PASSWORD_RE.test(pw);
}

export function passwordErrorMessage(pw: string | null | undefined): string | null {
  if (!pw) return 'La contraseña es requerida.';
  if (pw.length < 8 || pw.length > 12) return 'La contraseña debe tener entre 8 y 12 caracteres.';
  if (!/[a-z]/.test(pw)) return 'La contraseña debe contener al menos una letra minúscula.';
  if (!/[A-Z]/.test(pw)) return 'La contraseña debe contener al menos una letra mayúscula.';
  if (!/\d/.test(pw)) return 'La contraseña debe contener al menos un número.';
  if (!/^[A-Za-z0-9]+$/.test(pw)) return 'La contraseña debe ser alfanumérica.';
  return null;
}
