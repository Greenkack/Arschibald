"""
PDF Compression API Endpoints

Provides REST API endpoints for PDF compression and optimization operations.

Requirements: 1.3, 11.3
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

from ...services.pdf_compression_service import pdf_compression_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pdf-compression", tags=["PDF Compression"])


class CompressionOptions(BaseModel):
    """Options for PDF compression"""
    compression_level: int = Field(9, ge=0, le=9, description="Compression level (0-9)")
    optimize_images: bool = Field(True, description="Optimize images in PDF")
    image_quality: int = Field(85, ge=1, le=100, description="JPEG quality for images")
    image_dpi: int = Field(150, ge=72, le=300, description="Target DPI for images")
    remove_duplicates: bool = Field(True, description="Remove duplicate objects")
    compress_streams: bool = Field(True, description="Compress content streams")


class FontOptimizationOptions(BaseModel):
    """Options for font optimization"""
    subset_fonts: bool = Field(True, description="Create font subsets")
    embed_fonts: bool = Field(True, description="Embed fonts in PDF")


class EncryptionOptions(BaseModel):
    """Options for PDF encryption"""
    user_password: Optional[str] = Field(None, description="Password for opening PDF")
    owner_password: Optional[str] = Field(None, description="Password for modifying permissions")
    allow_print: bool = Field(True, description="Allow printing")
    allow_modify: bool = Field(False, description="Allow modifications")
    allow_copy: bool = Field(False, description="Allow copying content")
    allow_annotate: bool = Field(False, description="Allow annotations")


class MetadataOptions(BaseModel):
    """Options for metadata management"""
    title: Optional[str] = None
    author: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[str] = None
    creator: Optional[str] = "Solar Calculator Pro"
    producer: Optional[str] = "PDF Compression Service"
    remove_existing: bool = Field(False, description="Remove existing metadata")


class CompleteOptimizationOptions(BaseModel):
    """Options for complete PDF optimization"""
    compression_level: int = Field(9, ge=0, le=9)
    optimize_images: bool = True
    image_quality: int = Field(85, ge=1, le=100)
    image_dpi: int = Field(150, ge=72, le=300)
    remove_duplicates: bool = True
    compress_streams: bool = True
    optimize_fonts: bool = True
    subset_fonts: bool = True
    embed_fonts: bool = True
    add_metadata: bool = True
    metadata: Optional[Dict[str, str]] = None


@router.post("/compress")
async def compress_pdf(
    file: UploadFile = File(...),
    options: CompressionOptions = CompressionOptions()
):
    """
    Compress a PDF file
    
    - **file**: PDF file to compress
    - **options**: Compression options
    
    Returns compressed PDF file
    """
    try:
        logger.info(f"Compressing PDF: {file.filename}")
        
        # Read file
        pdf_bytes = await file.read()
        
        # Compress PDF
        compressed_pdf = pdf_compression_service.compress_pdf(
            pdf_bytes,
            compression_level=options.compression_level,
            optimize_images=options.optimize_images,
            image_quality=options.image_quality,
            image_dpi=options.image_dpi,
            remove_duplicates=options.remove_duplicates,
            compress_streams=options.compress_streams
        )
        
        # Calculate statistics
        original_size = len(pdf_bytes)
        compressed_size = len(compressed_pdf)
        reduction = (1 - compressed_size / original_size) * 100
        
        logger.info(
            f"PDF compressed: {original_size} -> {compressed_size} bytes "
            f"({reduction:.1f}% reduction)"
        )
        
        # Return compressed PDF
        return Response(
            content=compressed_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=compressed_{file.filename}",
                "X-Original-Size": str(original_size),
                "X-Compressed-Size": str(compressed_size),
                "X-Reduction-Percent": f"{reduction:.1f}"
            }
        )
        
    except Exception as e:
        logger.error(f"PDF compression failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF compression failed: {str(e)}")


@router.post("/optimize-fonts")
async def optimize_fonts(
    file: UploadFile = File(...),
    options: FontOptimizationOptions = FontOptimizationOptions()
):
    """
    Optimize fonts in a PDF file
    
    - **file**: PDF file to optimize
    - **options**: Font optimization options
    
    Returns PDF with optimized fonts
    """
    try:
        logger.info(f"Optimizing fonts in PDF: {file.filename}")
        
        # Read file
        pdf_bytes = await file.read()
        
        # Optimize fonts
        optimized_pdf = pdf_compression_service.optimize_fonts(
            pdf_bytes,
            subset_fonts=options.subset_fonts,
            embed_fonts=options.embed_fonts
        )
        
        logger.info("Font optimization complete")
        
        # Return optimized PDF
        return Response(
            content=optimized_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=optimized_{file.filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Font optimization failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Font optimization failed: {str(e)}")


@router.post("/stream")
async def stream_pdf(
    file: UploadFile = File(...),
    chunk_size: int = 8192
):
    """
    Stream a PDF file in chunks
    
    - **file**: PDF file to stream
    - **chunk_size**: Size of each chunk in bytes
    
    Returns streaming response
    """
    try:
        logger.info(f"Streaming PDF: {file.filename}")
        
        # Read file
        pdf_bytes = await file.read()
        
        # Create streaming response
        return StreamingResponse(
            pdf_compression_service.stream_pdf(pdf_bytes, chunk_size=chunk_size),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={file.filename}",
                "X-Chunk-Size": str(chunk_size)
            }
        )
        
    except Exception as e:
        logger.error(f"PDF streaming failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF streaming failed: {str(e)}")


@router.post("/encrypt")
async def encrypt_pdf(
    file: UploadFile = File(...),
    options: EncryptionOptions = EncryptionOptions()
):
    """
    Encrypt a PDF file with password protection
    
    - **file**: PDF file to encrypt
    - **options**: Encryption options
    
    Returns encrypted PDF file
    """
    try:
        logger.info(f"Encrypting PDF: {file.filename}")
        
        # Read file
        pdf_bytes = await file.read()
        
        # Prepare permissions
        permissions = {
            'print': options.allow_print,
            'modify': options.allow_modify,
            'copy': options.allow_copy,
            'annotate': options.allow_annotate
        }
        
        # Encrypt PDF
        encrypted_pdf = pdf_compression_service.encrypt_pdf(
            pdf_bytes,
            user_password=options.user_password,
            owner_password=options.owner_password,
            permissions=permissions
        )
        
        logger.info("PDF encryption complete")
        
        # Return encrypted PDF
        return Response(
            content=encrypted_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=encrypted_{file.filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"PDF encryption failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PDF encryption failed: {str(e)}")


@router.post("/metadata")
async def manage_metadata(
    file: UploadFile = File(...),
    options: MetadataOptions = MetadataOptions()
):
    """
    Manage PDF metadata
    
    - **file**: PDF file to update
    - **options**: Metadata options
    
    Returns PDF with updated metadata
    """
    try:
        logger.info(f"Managing metadata for PDF: {file.filename}")
        
        # Read file
        pdf_bytes = await file.read()
        
        # Prepare metadata
        metadata = {}
        if options.title:
            metadata['/Title'] = options.title
        if options.author:
            metadata['/Author'] = options.author
        if options.subject:
            metadata['/Subject'] = options.subject
        if options.keywords:
            metadata['/Keywords'] = options.keywords
        if options.creator:
            metadata['/Creator'] = options.creator
        if options.producer:
            metadata['/Producer'] = options.producer
        
        # Update metadata
        updated_pdf = pdf_compression_service.manage_metadata(
            pdf_bytes,
            metadata=metadata if metadata else None,
            remove_metadata=options.remove_existing
        )
        
        logger.info("Metadata management complete")
        
        # Return updated PDF
        return Response(
            content=updated_pdf,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=metadata_{file.filename}"
            }
        )
        
    except Exception as e:
        logger.error(f"Metadata management failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Metadata management failed: {str(e)}")


@router.get("/info")
async def get_pdf_info(file: UploadFile = File(...)):
    """
    Get information about a PDF file
    
    - **file**: PDF file to analyze
    
    Returns PDF information
    """
    try:
        logger.info(f"Getting info for PDF: {file.filename}")
        
        # Read file
        pdf_bytes = await file.read()
        
        # Get info
        info = pdf_compression_service.get_pdf_info(pdf_bytes)
        
        return {
            "filename": file.filename,
            **info
        }
        
    except Exception as e:
        logger.error(f"Failed to get PDF info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get PDF info: {str(e)}")


@router.post("/optimize-complete")
async def optimize_complete(
    file: UploadFile = File(...),
    options: CompleteOptimizationOptions = CompleteOptimizationOptions()
):
    """
    Complete PDF optimization with all available techniques
    
    - **file**: PDF file to optimize
    - **options**: Complete optimization options
    
    Returns fully optimized PDF with statistics
    """
    try:
        logger.info(f"Starting complete optimization for PDF: {file.filename}")
        
        # Read file
        pdf_bytes = await file.read()
        
        # Prepare options
        opt_dict = options.dict()
        
        # Perform complete optimization
        result = pdf_compression_service.optimize_pdf_complete(
            pdf_bytes,
            options=opt_dict
        )
        
        logger.info(
            f"Complete optimization finished: "
            f"{result['size_reduction_percent']:.1f}% reduction"
        )
        
        # Return optimized PDF with statistics in headers
        return Response(
            content=result['optimized_pdf'],
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=optimized_{file.filename}",
                "X-Original-Size": str(result['original_size_bytes']),
                "X-Optimized-Size": str(result['optimized_size_bytes']),
                "X-Size-Reduction": str(result['size_reduction_bytes']),
                "X-Reduction-Percent": f"{result['size_reduction_percent']:.1f}",
                "X-Original-Pages": str(result['original_info']['num_pages']),
                "X-Optimized-Pages": str(result['optimized_info']['num_pages'])
            }
        )
        
    except Exception as e:
        logger.error(f"Complete optimization failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Complete optimization failed: {str(e)}")
