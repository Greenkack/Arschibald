/**
 * Language Switcher Component
 * Allows users to change the application language
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Dropdown } from 'primereact/dropdown';
import { Button } from 'primereact/button';
import { Dialog } from 'primereact/dialog';
import { supportedLanguages, SupportedLanguage } from '../../i18n/i18nConfig';
import './LanguageSwitcher.css';

interface LanguageOption {
  code: SupportedLanguage;
  name: string;
  nativeName: string;
  flag: string;
}

export const LanguageSwitcher: React.FC<{
  variant?: 'dropdown' | 'button' | 'menu';
  showFlag?: boolean;
  showNativeName?: boolean;
}> = ({ variant = 'dropdown', showFlag = true, showNativeName = true }) => {
  const { i18n, t } = useTranslation();
  const [showDialog, setShowDialog] = useState(false);

  const languageOptions: LanguageOption[] = Object.entries(supportedLanguages).map(
    ([code, info]) => ({
      code: code as SupportedLanguage,
      name: info.name,
      nativeName: info.nativeName,
      flag: info.flag,
    })
  );

  const currentLanguage = languageOptions.find(
    (lang) => lang.code === i18n.language
  ) || languageOptions[0];

  const handleLanguageChange = async (languageCode: SupportedLanguage) => {
    await i18n.changeLanguage(languageCode);
    
    // Update document direction for RTL languages
    const isRTL = supportedLanguages[languageCode].rtl;
    document.documentElement.dir = isRTL ? 'rtl' : 'ltr';
    document.documentElement.lang = languageCode;
    
    // Store preference
    localStorage.setItem('i18nextLng', languageCode);
    
    // Notify backend
    try {
      await fetch('/api/v1/user/language', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ language: languageCode }),
      });
    } catch (error) {
      console.error('Failed to save language preference:', error);
    }
  };

  const languageTemplate = (option: LanguageOption) => (
    <div className="language-option">
      {showFlag && <span className="language-flag">{option.flag}</span>}
      <span className="language-name">
        {showNativeName ? option.nativeName : option.name}
      </span>
    </div>
  );

  const selectedTemplate = (option: LanguageOption) => {
    if (!option) return null;
    return (
      <div className="language-selected">
        {showFlag && <span className="language-flag">{option.flag}</span>}
        <span className="language-code">{option.code.toUpperCase()}</span>
      </div>
    );
  };

  if (variant === 'dropdown') {
    return (
      <Dropdown
        value={currentLanguage}
        options={languageOptions}
        onChange={(e) => handleLanguageChange(e.value.code)}
        optionLabel="nativeName"
        itemTemplate={languageTemplate}
        valueTemplate={selectedTemplate}
        className="language-switcher-dropdown"
        placeholder={t('common.language')}
      />
    );
  }

  if (variant === 'button') {
    return (
      <>
        <Button
          icon="pi pi-globe"
          label={currentLanguage.flag}
          onClick={() => setShowDialog(true)}
          className="language-switcher-button p-button-text"
          tooltip={t('common.language')}
        />
        <Dialog
          header={t('common.language')}
          visible={showDialog}
          onHide={() => setShowDialog(false)}
          className="language-dialog"
        >
          <div className="language-grid">
            {languageOptions.map((lang) => (
              <Button
                key={lang.code}
                className={`language-card ${
                  lang.code === currentLanguage.code ? 'active' : ''
                }`}
                onClick={() => {
                  handleLanguageChange(lang.code);
                  setShowDialog(false);
                }}
              >
                <div className="language-card-content">
                  <span className="language-card-flag">{lang.flag}</span>
                  <span className="language-card-name">{lang.nativeName}</span>
                  {lang.code === currentLanguage.code && (
                    <i className="pi pi-check language-card-check" />
                  )}
                </div>
              </Button>
            ))}
          </div>
        </Dialog>
      </>
    );
  }

  // Menu variant
  return (
    <div className="language-switcher-menu">
      {languageOptions.map((lang) => (
        <Button
          key={lang.code}
          className={`language-menu-item ${
            lang.code === currentLanguage.code ? 'active' : ''
          }`}
          onClick={() => handleLanguageChange(lang.code)}
        >
          {languageTemplate(lang)}
        </Button>
      ))}
    </div>
  );
};

export default LanguageSwitcher;
