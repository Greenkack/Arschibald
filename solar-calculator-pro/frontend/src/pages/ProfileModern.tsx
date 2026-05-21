/**
 * Modern User Profile Page with shadcn/ui
 * 
 * Display and edit user profile information
 */

import React, { useState } from 'react';
import { User as UserIcon, Mail, Edit2, Save, X, Camera } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { useAuth } from '@hooks/useAuth';

interface ProfileFormData {
  username: string;
  email: string;
}

interface ProfileFormErrors {
  username?: string;
  email?: string;
}

const ProfileModern: React.FC = () => {
  const { user, refreshUser } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [formData, setFormData] = useState<ProfileFormData>({
    username: user?.username || '',
    email: user?.email || '',
  });

  const [formErrors, setFormErrors] = useState<ProfileFormErrors>({});

  /**
   * Validate email format
   */
  const validateEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  /**
   * Validate form field
   */
  const validateField = (name: keyof ProfileFormData, value: string): string | undefined => {
    switch (name) {
      case 'username':
        if (!value.trim()) {
          return 'Benutzername ist erforderlich';
        }
        if (value.length < 3) {
          return 'Benutzername muss mindestens 3 Zeichen lang sein';
        }
        break;
      case 'email':
        if (!value.trim()) {
          return 'E-Mail ist erforderlich';
        }
        if (!validateEmail(value)) {
          return 'Bitte geben Sie eine gültige E-Mail-Adresse ein';
        }
        break;
    }
    return undefined;
  };

  /**
   * Validate entire form
   */
  const validateForm = (): boolean => {
    const errors: ProfileFormErrors = {};
    
    const usernameError = validateField('username', formData.username);
    if (usernameError) errors.username = usernameError;
    
    const emailError = validateField('email', formData.email);
    if (emailError) errors.email = emailError;

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  /**
   * Handle input change
   */
  const handleChange = (field: keyof ProfileFormData, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));

    // Clear error for this field
    const error = validateField(field, value);
    setFormErrors((prev) => ({
      ...prev,
      [field]: error,
    }));

    // Clear messages
    setSuccessMessage(null);
    setErrorMessage(null);
  };

  /**
   * Handle edit button click
   */
  const handleEdit = () => {
    setIsEditing(true);
    setSuccessMessage(null);
    setErrorMessage(null);
  };

  /**
   * Handle cancel button click
   */
  const handleCancel = () => {
    setIsEditing(false);
    setFormData({
      username: user?.username || '',
      email: user?.email || '',
    });
    setFormErrors({});
    setSuccessMessage(null);
    setErrorMessage(null);
  };

  /**
   * Handle save button click
   */
  const handleSave = async () => {
    if (!validateForm()) {
      return;
    }

    setIsSaving(true);
    setSuccessMessage(null);
    setErrorMessage(null);

    try {
      // Simulate API call (replace with actual API call)
      await new Promise((resolve) => setTimeout(resolve, 1000));
      
      // In real implementation, make API call to update user profile
      // await api.put('/api/v1/users/profile', formData);
      
      setSuccessMessage('Profil erfolgreich aktualisiert');
      setIsEditing(false);
      
      // Refresh user data if needed
      if (refreshUser) {
        await refreshUser();
      }
    } catch (error) {
      setErrorMessage('Fehler beim Aktualisieren des Profils');
      console.error('Profile update error:', error);
    } finally {
      setIsSaving(false);
    }
  };

  // Get user initials for avatar
  const getInitials = (name: string): string => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="space-y-6">
      {/* Messages */}
      {successMessage && (
        <Alert>
          <AlertDescription>{successMessage}</AlertDescription>
        </Alert>
      )}
      {errorMessage && (
        <Alert variant="destructive">
          <AlertDescription>{errorMessage}</AlertDescription>
        </Alert>
      )}

      {/* Profile Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Profilinformationen</CardTitle>
              <CardDescription>
                Verwalten Sie Ihre persönlichen Informationen
              </CardDescription>
            </div>
            {!isEditing ? (
              <Button onClick={handleEdit} variant="outline" size="sm">
                <Edit2 className="mr-2 h-4 w-4" />
                Bearbeiten
              </Button>
            ) : (
              <div className="flex gap-2">
                <Button onClick={handleCancel} variant="outline" size="sm" disabled={isSaving}>
                  <X className="mr-2 h-4 w-4" />
                  Abbrechen
                </Button>
                <Button onClick={handleSave} size="sm" disabled={isSaving}>
                  <Save className="mr-2 h-4 w-4" />
                  {isSaving ? 'Speichern...' : 'Speichern'}
                </Button>
              </div>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Avatar Section */}
          <div className="flex items-center gap-6">
            <div className="relative">
              <Avatar className="h-24 w-24">
                <AvatarFallback className="text-2xl">
                  {getInitials(user?.username || 'User')}
                </AvatarFallback>
              </Avatar>
              {isEditing && (
                <Button
                  size="icon"
                  variant="secondary"
                  className="absolute bottom-0 right-0 h-8 w-8 rounded-full"
                >
                  <Camera className="h-4 w-4" />
                </Button>
              )}
            </div>
            <div>
              <h3 className="text-lg font-semibold">{user?.username}</h3>
              <p className="text-sm text-muted-foreground">{user?.email}</p>
              <p className="mt-1 text-xs text-muted-foreground">
                Mitglied seit {new Date(user?.created_at || Date.now()).toLocaleDateString('de-DE')}
              </p>
            </div>
          </div>

          <Separator />

          {/* Form Fields */}
          <div className="grid gap-4">
            {/* Username */}
            <div className="grid gap-2">
              <Label htmlFor="username">Benutzername</Label>
              <div className="relative">
                <UserIcon className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="username"
                  type="text"
                  value={formData.username}
                  onChange={(e) => handleChange('username', e.target.value)}
                  disabled={!isEditing || isSaving}
                  className={`pl-9 ${formErrors.username ? 'border-destructive' : ''}`}
                />
              </div>
              {formErrors.username && (
                <p className="text-sm text-destructive">{formErrors.username}</p>
              )}
            </div>

            {/* Email */}
            <div className="grid gap-2">
              <Label htmlFor="email">E-Mail</Label>
              <div className="relative">
                <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => handleChange('email', e.target.value)}
                  disabled={!isEditing || isSaving}
                  className={`pl-9 ${formErrors.email ? 'border-destructive' : ''}`}
                />
              </div>
              {formErrors.email && (
                <p className="text-sm text-destructive">{formErrors.email}</p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Additional Information Card */}
      <Card>
        <CardHeader>
          <CardTitle>Kontoinformationen</CardTitle>
          <CardDescription>
            Details zu Ihrem Konto und Ihrer Aktivität
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium">Rolle</p>
                <p className="text-sm text-muted-foreground">{user?.role || 'Benutzer'}</p>
              </div>
              <div>
                <p className="text-sm font-medium">Status</p>
                <p className="text-sm text-muted-foreground">
                  <span className="inline-flex items-center rounded-full bg-green-50 px-2 py-1 text-xs font-medium text-green-700 ring-1 ring-inset ring-green-600/20">
                    Aktiv
                  </span>
                </p>
              </div>
            </div>
            <Separator />
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium">Account erstellt</p>
                <p className="text-sm text-muted-foreground">
                  {new Date(user?.created_at || Date.now()).toLocaleString('de-DE')}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium">Account-ID</p>
                <p className="text-sm font-mono text-muted-foreground">
                  {user?.id || 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProfileModern;
