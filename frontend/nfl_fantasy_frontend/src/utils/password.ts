import { PASSWORD_CONFIG } from '../config/constants';

export const PASSWORD_RE = PASSWORD_CONFIG.PATTERN;

export function isValidPassword(pw: string): boolean {
  return PASSWORD_RE.test(pw);
}

export function passwordErrorMessage(pw: string | null | undefined): string | null {
  if (!pw) return 'La contraseña es requerida.';
  if (pw.length < PASSWORD_CONFIG.MIN_LENGTH || pw.length > PASSWORD_CONFIG.MAX_LENGTH) {
    return `La contraseña debe tener entre ${PASSWORD_CONFIG.MIN_LENGTH} y ${PASSWORD_CONFIG.MAX_LENGTH} caracteres.`;
  }
  if (!/[a-z]/.test(pw)) return `La contraseña debe contener ${PASSWORD_CONFIG.RULES.LOWERCASE}.`;
  if (!/[A-Z]/.test(pw)) return `La contraseña debe contener ${PASSWORD_CONFIG.RULES.UPPERCASE}.`;
  if (!/\d/.test(pw)) return `La contraseña debe contener ${PASSWORD_CONFIG.RULES.DIGIT}.`;
  if (!/^[A-Za-z0-9]+$/.test(pw)) return `La contraseña debe ser ${PASSWORD_CONFIG.RULES.ALPHANUMERIC}.`;
  return null;
}
