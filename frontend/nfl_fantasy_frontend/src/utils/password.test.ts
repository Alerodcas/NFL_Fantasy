import { describe, it, expect } from 'vitest';
import { isValidPassword, passwordErrorMessage } from './password';
import { PASSWORD_CONFIG } from '../config/constants';

describe('Password Validation Utils', () => {
  
  // ==============================
  // isValidPassword Tests
  // ==============================
  
  describe('isValidPassword', () => {
    it('should return true for valid passwords', () => {
      expect(isValidPassword('Pass1234')).toBe(true);
      expect(isValidPassword('Test5678')).toBe(true);
      expect(isValidPassword('Abc12345')).toBe(true);
      expect(isValidPassword('Valid123')).toBe(true);
    });

    it('should return false for passwords too short', () => {
      expect(isValidPassword('Pass12')).toBe(false);  // 6 chars
      expect(isValidPassword('Test1')).toBe(false);   // 5 chars
    });

    it('should return false for passwords too long', () => {
      expect(isValidPassword('Password12345')).toBe(false);  // 13 chars
      expect(isValidPassword('VeryLongPass123')).toBe(false); // 15 chars
    });

    it('should return false for passwords without lowercase', () => {
      expect(isValidPassword('PASSWORD123')).toBe(false);
      expect(isValidPassword('TEST5678')).toBe(false);
    });

    it('should return false for passwords without uppercase', () => {
      expect(isValidPassword('password123')).toBe(false);
      expect(isValidPassword('test5678')).toBe(false);
    });

    it('should return false for passwords without digits', () => {
      expect(isValidPassword('Password')).toBe(false);
      expect(isValidPassword('TestPass')).toBe(false);
    });

    it('should return false for passwords with special characters', () => {
      expect(isValidPassword('Pass123!')).toBe(false);
      expect(isValidPassword('Test@5678')).toBe(false);
      expect(isValidPassword('Valid#123')).toBe(false);
    });

    it('should return false for empty string', () => {
      expect(isValidPassword('')).toBe(false);
    });
  });

  // ==============================
  // passwordErrorMessage Tests
  // ==============================
  
  describe('passwordErrorMessage', () => {
    it('should return null for valid passwords', () => {
      expect(passwordErrorMessage('Pass1234')).toBeNull();
      expect(passwordErrorMessage('Test5678')).toBeNull();
      expect(passwordErrorMessage('Valid123')).toBeNull();
    });

    it('should return error for null/undefined', () => {
      expect(passwordErrorMessage(null)).toBe('La contraseña es requerida.');
      expect(passwordErrorMessage(undefined)).toBe('La contraseña es requerida.');
    });

    it('should return error for empty string', () => {
      expect(passwordErrorMessage('')).toBe('La contraseña es requerida.');
    });

    it('should return error for passwords too short', () => {
      const error = passwordErrorMessage('Pass12');
      expect(error).toBe('La contraseña debe tener entre 8 y 12 caracteres.');
    });

    it('should return error for passwords too long', () => {
      const error = passwordErrorMessage('Password12345');
      expect(error).toBe('La contraseña debe tener entre 8 y 12 caracteres.');
    });

    it('should return error for missing lowercase', () => {
      const error = passwordErrorMessage('PASSWORD123');
      expect(error).toBe('La contraseña debe contener al menos una letra minúscula.');
    });

    it('should return error for missing uppercase', () => {
      const error = passwordErrorMessage('password123');
      expect(error).toBe('La contraseña debe contener al menos una letra mayúscula.');
    });

    it('should return error for missing digit', () => {
      const error = passwordErrorMessage('Password');
      expect(error).toBe('La contraseña debe contener al menos un número.');
    });

    it('should return error for special characters', () => {
      const error = passwordErrorMessage('Pass123!');
      expect(error).toBe('La contraseña debe ser alfanumérica.');
    });

    it('should prioritize length error over other errors', () => {
      // Too short AND missing uppercase - length error comes first
      const error = passwordErrorMessage('pass12');
      expect(error).toBe('La contraseña debe tener entre 8 y 12 caracteres.');
    });

    it('should check lowercase before uppercase', () => {
      // 8-12 chars, has digit, but missing lowercase
      const error = passwordErrorMessage('PASSWORD123');
      expect(error).toBe('La contraseña debe contener al menos una letra minúscula.');
    });
  });
});
