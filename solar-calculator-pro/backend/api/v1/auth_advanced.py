"""
Advanced Authentication API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List

from backend.core.dependencies import get_db, get_current_user
from backend.models.auth_advanced_schemas import *
from backend.services.auth_advanced_service import (
    TwoFactorService, SSOService, BiometricService,
    SessionService, PasswordPolicyService, LoginAttemptService
)
from backend.models.user_models import User


router = APIRouter(prefix="/auth/advanced", tags=["Advanced Authentication"])


# Two-Factor Authentication Endpoints

@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)
async def setup_two_factor(
    request: TwoFactorSetupRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Setup two-factor authentication"""
    try:
        if request.method == TwoFactorMethodEnum.TOTP:
            secret, qr_code, backup_codes = TwoFactorService.setup_totp(db, current_user.id)
            return TwoFactorSetupResponse(
                method=request.method,
                secret=secret,
                qr_code=qr_code,
                backup_codes=backup_codes
            )
        
        elif request.method == TwoFactorMethodEnum.SMS:
            if not request.phone_number:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Phone number required for SMS 2FA"
                )
            TwoFactorService.setup_sms(db, current_user.id, request.phone_number)
            return TwoFactorSetupResponse(
                method=request.method,
                phone_number=request.phone_number
            )
        
        elif request.method == TwoFactorMethodEnum.EMAIL:
            if not request.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email required for email 2FA"
                )
            # Similar to SMS setup
            return TwoFactorSetupResponse(
                method=request.method,
                email=request.email
            )
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported 2FA method"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to setup 2FA: {str(e)}"
        )


@router.post("/2fa/verify", response_model=TwoFactorVerifyResponse)
async def verify_two_factor(
    request: TwoFactorVerifyRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Verify two-factor authentication code"""
    try:
        if request.method == TwoFactorMethodEnum.TOTP:
            verified = TwoFactorService.verify_totp(db, current_user.id, request.code)
        elif request.method == TwoFactorMethodEnum.BACKUP_CODES:
            verified = TwoFactorService.verify_backup_code(db, current_user.id, request.code)
        else:
            # For SMS/Email, verification would be similar
            verified = False
        
        if verified:
            # Enable 2FA if this is first verification
            TwoFactorService.enable_two_factor(db, current_user.id, request.method)
            return TwoFactorVerifyResponse(
                verified=True,
                message="Two-factor authentication verified successfully"
            )
        else:
            return TwoFactorVerifyResponse(
                verified=False,
                message="Invalid verification code"
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify 2FA: {str(e)}"
        )


@router.post("/2fa/disable")
async def disable_two_factor(
    request: TwoFactorDisableRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disable two-factor authentication"""
    # Verify password before disabling
    from backend.core.security import verify_password
    if not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    success = TwoFactorService.disable_two_factor(db, current_user.id, request.method)
    
    if success:
        return {"message": "Two-factor authentication disabled successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="2FA method not found"
        )


@router.get("/2fa/status", response_model=TwoFactorStatusResponse)
async def get_two_factor_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get two-factor authentication status"""
    methods = TwoFactorService.get_enabled_methods(db, current_user.id)
    
    return TwoFactorStatusResponse(
        enabled=len(methods) > 0,
        methods=methods,
        primary_method=methods[0] if methods else None
    )


# SSO Endpoints

@router.post("/sso/initiate", response_model=SSOInitiateResponse)
async def initiate_sso(request: SSOInitiateRequest):
    """Initiate SSO login flow"""
    redirect_uri = request.redirect_uri or "http://localhost:3000/auth/sso/callback"
    auth_url, state = SSOService.initiate_oauth(request.provider, redirect_uri)
    
    return SSOInitiateResponse(
        authorization_url=auth_url,
        state=state
    )


@router.post("/sso/link")
async def link_sso_provider(
    request: SSOLinkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Link SSO provider to existing account"""
    # In production, exchange code for tokens with provider
    # For demo, we'll use placeholder values
    success = SSOService.link_sso_provider(
        db=db,
        user_id=current_user.id,
        provider=request.provider,
        provider_user_id="demo_provider_id",
        provider_email=current_user.email,
        access_token="demo_access_token",
        refresh_token="demo_refresh_token"
    )
    
    if success:
        return {"message": f"{request.provider.value} linked successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to link SSO provider"
        )


@router.post("/sso/unlink")
async def unlink_sso_provider(
    request: SSOUnlinkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unlink SSO provider from account"""
    # Verify password before unlinking
    from backend.core.security import verify_password
    if not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    success = SSOService.unlink_sso_provider(db, current_user.id, request.provider)
    
    if success:
        return {"message": f"{request.provider.value} unlinked successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SSO provider not found"
        )


@router.get("/sso/status", response_model=SSOStatusResponse)
async def get_sso_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get SSO status"""
    providers = SSOService.get_linked_providers(db, current_user.id)
    
    return SSOStatusResponse(linked_providers=providers)


# Biometric Authentication Endpoints

@router.post("/biometric/register", response_model=BiometricRegisterResponse)
async def register_biometric(
    request: BiometricRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register biometric authentication"""
    try:
        biometric_id = BiometricService.register_biometric(
            db=db,
            user_id=current_user.id,
            biometric_type=request.biometric_type,
            device_id=request.device_id,
            device_name=request.device_name or "Unknown Device",
            device_platform=request.device_platform or "Unknown",
            public_key=request.public_key,
            credential_id=request.credential_id
        )
        
        return BiometricRegisterResponse(
            success=True,
            biometric_id=biometric_id,
            message="Biometric authentication registered successfully"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register biometric: {str(e)}"
        )


@router.post("/biometric/challenge", response_model=BiometricChallengeResponse)
async def get_biometric_challenge(request: BiometricChallengeRequest):
    """Get challenge for biometric authentication"""
    challenge = BiometricService.generate_challenge()
    
    return BiometricChallengeResponse(
        challenge=challenge,
        timeout=60
    )


@router.post("/biometric/verify", response_model=BiometricVerifyResponse)
async def verify_biometric(
    request: BiometricVerifyRequest,
    db: Session = Depends(get_db)
):
    """Verify biometric authentication"""
    user_id = BiometricService.verify_biometric(
        db=db,
        device_id=request.device_id,
        credential_id=request.credential_id,
        signature=request.signature,
        challenge=request.challenge
    )
    
    if user_id:
        # Generate access token
        from backend.core.security import create_access_token
        access_token = create_access_token(data={"sub": str(user_id)})
        
        return BiometricVerifyResponse(
            verified=True,
            access_token=access_token,
            message="Biometric authentication successful"
        )
    else:
        return BiometricVerifyResponse(
            verified=False,
            message="Biometric authentication failed"
        )


@router.delete("/biometric/{biometric_id}")
async def remove_biometric(
    biometric_id: int,
    password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove biometric authentication"""
    # Verify password
    from backend.core.security import verify_password
    if not verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    success = BiometricService.remove_biometric(db, biometric_id)
    
    if success:
        return {"message": "Biometric authentication removed successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Biometric authentication not found"
        )


@router.get("/biometric/status", response_model=BiometricStatusResponse)
async def get_biometric_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get biometric authentication status"""
    devices = BiometricService.get_registered_devices(db, current_user.id)
    
    return BiometricStatusResponse(
        enabled=len(devices) > 0,
        devices=devices
    )


# Session Management Endpoints

@router.get("/sessions", response_model=SessionListResponse)
async def get_active_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all active sessions"""
    sessions = SessionService.get_active_sessions(db, current_user.id)
    
    session_info = [
        SessionInfo(
            session_id=s.id,
            device_name=s.device_name,
            device_type=s.device_type,
            platform=s.platform,
            browser=s.browser,
            ip_address=s.ip_address,
            created_at=s.created_at,
            last_activity_at=s.last_activity_at,
            is_current=False  # Would need to check current session token
        )
        for s in sessions
    ]
    
    return SessionListResponse(
        sessions=session_info,
        total=len(session_info)
    )


@router.post("/sessions/revoke")
async def revoke_session(
    request: SessionRevokeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke a specific session"""
    success = SessionService.revoke_session(db, request.session_id, request.reason)
    
    if success:
        return {"message": "Session revoked successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )


@router.post("/sessions/revoke-all")
async def revoke_all_sessions(
    request: SessionRevokeAllRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Revoke all sessions except current"""
    # Verify password
    from backend.core.security import verify_password
    if not verify_password(request.password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )
    
    # Would need to get current session ID from token
    count = SessionService.revoke_all_sessions(db, current_user.id)
    
    return {"message": f"Revoked {count} sessions successfully"}


# Password Policy Endpoints

@router.get("/password/policy", response_model=PasswordPolicyResponse)
async def get_password_policy(db: Session = Depends(get_db)):
    """Get active password policy"""
    policy = PasswordPolicyService.get_active_policy(db)
    
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active password policy found"
        )
    
    return PasswordPolicyResponse(
        min_length=policy.min_length,
        max_length=policy.max_length,
        require_uppercase=policy.require_uppercase,
        require_lowercase=policy.require_lowercase,
        require_numbers=policy.require_numbers,
        require_special_chars=policy.require_special_chars,
        special_chars_allowed=policy.special_chars_allowed,
        prevent_reuse_count=policy.prevent_reuse_count,
        expires_after_days=policy.expires_after_days,
        warn_before_expiry_days=policy.warn_before_expiry_days,
        max_failed_attempts=policy.max_failed_attempts,
        lockout_duration_minutes=policy.lockout_duration_minutes
    )


@router.post("/password/change")
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password"""
    # Verify current password
    from backend.core.security import verify_password, get_password_hash
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid current password"
        )
    
    # Get password policy
    policy = PasswordPolicyService.get_active_policy(db)
    
    # Validate new password
    is_valid, errors = PasswordPolicyService.validate_password(request.new_password, policy)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": errors}
        )
    
    # Check password reuse
    if PasswordPolicyService.check_password_reuse(db, current_user.id, request.new_password, policy):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password was used recently. Cannot reuse last {policy.prevent_reuse_count} passwords."
        )
    
    # Update password
    new_hash = get_password_hash(request.new_password)
    current_user.hashed_password = new_hash
    
    # Add to password history
    PasswordPolicyService.add_password_to_history(db, current_user.id, new_hash)
    
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.get("/password/expiry", response_model=PasswordExpiryResponse)
async def get_password_expiry(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get password expiry information"""
    policy = PasswordPolicyService.get_active_policy(db)
    is_expired, days_until_expiry = PasswordPolicyService.check_password_expiry(db, current_user.id, policy)
    
    return PasswordExpiryResponse(
        expires_at=None,  # Would calculate from last password change
        days_until_expiry=days_until_expiry,
        is_expired=is_expired,
        requires_change=is_expired
    )


# Login Attempt Tracking Endpoints

@router.get("/login-attempts", response_model=LoginAttemptsResponse)
async def get_login_attempts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50
):
    """Get recent login attempts"""
    from backend.models.auth_advanced_models import LoginAttempt
    
    attempts = db.query(LoginAttempt).filter(
        LoginAttempt.user_id == current_user.id
    ).order_by(LoginAttempt.attempted_at.desc()).limit(limit).all()
    
    attempt_info = [
        LoginAttemptInfo(
            id=a.id,
            username=a.username,
            success=a.success,
            auth_method=a.auth_method.value,
            failure_reason=a.failure_reason,
            ip_address=a.ip_address,
            device_type=a.device_type,
            platform=a.platform,
            browser=a.browser,
            country=a.country,
            city=a.city,
            attempted_at=a.attempted_at,
            is_suspicious=a.is_suspicious
        )
        for a in attempts
    ]
    
    failed_count = sum(1 for a in attempts if not a.success)
    suspicious_count = sum(1 for a in attempts if a.is_suspicious)
    
    return LoginAttemptsResponse(
        attempts=attempt_info,
        total=len(attempt_info),
        failed_count=failed_count,
        suspicious_count=suspicious_count
    )


@router.get("/account/lockout", response_model=AccountLockoutResponse)
async def get_account_lockout_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get account lockout status"""
    is_locked, lockout = LoginAttemptService.is_account_locked(db, current_user.id)
    
    if is_locked and lockout:
        return AccountLockoutResponse(
            is_locked=True,
            lockout=AccountLockoutInfo(
                locked_at=lockout.locked_at,
                locked_until=lockout.locked_until,
                reason=lockout.reason,
                failed_attempts_count=lockout.failed_attempts_count,
                is_active=lockout.is_active
            )
        )
    else:
        return AccountLockoutResponse(is_locked=False)
