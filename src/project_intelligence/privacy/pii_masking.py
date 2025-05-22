"""
PII masking module for Project Intelligence.

This module provides functionality for detecting and masking personally identifiable information (PII)
in text data to ensure GDPR compliance when processing and storing data.
"""

import logging
import re
from enum import Enum
from typing import Any, Dict, List, Optional, Pattern, Set, Tuple, Union

logger = logging.getLogger(__name__)


class PIIType(str, Enum):
    """Types of PII that can be detected and masked."""

    EMAIL = "email"
    PHONE = "phone"
    IP_ADDRESS = "ip_address"
    CREDIT_CARD = "credit_card"
    SSN = "ssn"
    PASSPORT = "passport"
    ADDRESS = "address"
    NAME = "name"
    DATE_OF_BIRTH = "date_of_birth"
    CUSTOM = "custom"


class PIIMaskingLevel(str, Enum):
    """
    Masking levels for PII data.
    
    - NONE: No masking is applied
    - PARTIAL: Partial masking, keeping some characters visible
    - FULL: Complete masking of the PII
    - HASH: Replace PII with a hash value
    - PSEUDONYMIZE: Replace PII with a consistent pseudonym
    """

    NONE = "none"
    PARTIAL = "partial"
    FULL = "full"
    HASH = "hash"
    PSEUDONYMIZE = "pseudonymize"


class PIIPattern:
    """Pattern for detecting a specific type of PII."""

    def __init__(
        self,
        pii_type: PIIType,
        regex: Union[str, Pattern],
        validation_func: Optional[callable] = None,
        description: Optional[str] = None,
    ):
        """
        Initialize a PII pattern.
        
        Args:
            pii_type: Type of PII this pattern detects
            regex: Regular expression for detecting the PII
            validation_func: Optional function for additional validation beyond regex
            description: Human-readable description of the pattern
        """
        self.pii_type = pii_type
        self.regex = re.compile(regex) if isinstance(regex, str) else regex
        self.validation_func = validation_func
        self.description = description

    def matches(self, text: str) -> List[Tuple[int, int]]:
        """
        Find all matches of this pattern in the text.
        
        Args:
            text: Text to search for PII
            
        Returns:
            List of (start, end) tuples for each match
        """
        matches = []
        for match in self.regex.finditer(text):
            start, end = match.span()
            match_text = text[start:end]
            
            # Apply additional validation if provided
            if self.validation_func is None or self.validation_func(match_text):
                matches.append((start, end))
                
        return matches


class PIIMasker:
    """
    Detects and masks PII in text data.
    
    This class provides methods for identifying different types of personally identifiable
    information in text and masking them according to configurable policies.
    """

    def __init__(self, patterns: Optional[List[PIIPattern]] = None):
        """
        Initialize the PII masker.
        
        Args:
            patterns: Optional list of custom PII patterns to use
        """
        self.patterns = patterns or self._get_default_patterns()
        self.pseudonym_map = {}  # For consistent pseudonymization
        
    def _get_default_patterns(self) -> List[PIIPattern]:
        """
        Get the default set of PII detection patterns.
        
        Returns:
            List of default PII patterns
        """
        return [
            PIIPattern(
                PIIType.EMAIL,
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                description="Email address"
            ),
            PIIPattern(
                PIIType.PHONE,
                r'\b(?:\+\d{1,3}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
                description="Phone number"
            ),
            PIIPattern(
                PIIType.IP_ADDRESS,
                r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
                lambda ip: all(0 <= int(octet) <= 255 for octet in ip.split('.')),
                description="IPv4 address"
            ),
            PIIPattern(
                PIIType.CREDIT_CARD,
                r'\b(?:\d{4}[- ]?){3}\d{4}\b',
                lambda cc: self._luhn_check(cc.replace('-', '').replace(' ', '')),
                description="Credit card number"
            ),
            PIIPattern(
                PIIType.SSN,
                r'\b\d{3}-\d{2}-\d{4}\b',
                description="US Social Security Number"
            ),
            PIIPattern(
                PIIType.PASSPORT,
                r'\b[A-Z]{1,2}\d{6,9}\b',
                description="Passport number"
            ),
            # Simplified address pattern - would need refinement in practice
            PIIPattern(
                PIIType.ADDRESS,
                r'\b\d+\s+[A-Za-z0-9\s,]+(?:Avenue|Lane|Road|Boulevard|Drive|Street|Ave|Dr|Rd|Blvd|Ln|St)\.?\b',
                description="Street address"
            ),
            # Date of birth patterns
            PIIPattern(
                PIIType.DATE_OF_BIRTH,
                r'\b(?:\d{1,2}[\/\-\.]\d{1,2}[\/\-\.]\d{2,4})|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b',
                description="Date of birth"
            ),
        ]

    def _luhn_check(self, number: str) -> bool:
        """
        Validate a number using the Luhn algorithm (for credit cards).
        
        Args:
            number: Number to validate
            
        Returns:
            True if the number passes the Luhn check
        """
        digits = [int(d) for d in number if d.isdigit()]
        if not digits:
            return False
            
        # Double every second digit from right to left
        for i in range(len(digits)-2, -1, -2):
            digits[i] *= 2
            if digits[i] > 9:
                digits[i] -= 9
                
        # Sum all digits
        total = sum(digits)
        
        # Valid if sum is divisible by 10
        return total % 10 == 0

    def detect_pii(self, text: str, pii_types: Optional[Set[PIIType]] = None) -> List[Dict[str, Any]]:
        """
        Detect PII in text.
        
        Args:
            text: Text to scan for PII
            pii_types: Optional set of PII types to detect (detects all types if None)
            
        Returns:
            List of dictionaries containing information about detected PII
        """
        results = []
        
        for pattern in self.patterns:
            # Skip if not in requested types
            if pii_types and pattern.pii_type not in pii_types:
                continue
                
            matches = pattern.matches(text)
            
            for start, end in matches:
                results.append({
                    "type": pattern.pii_type,
                    "start": start,
                    "end": end,
                    "value": text[start:end],
                    "description": pattern.description
                })
        
        # Sort by position in text
        results.sort(key=lambda x: x["start"])
        
        return results

    def mask_pii(
        self,
        text: str,
        masking_level: PIIMaskingLevel = PIIMaskingLevel.FULL,
        pii_types: Optional[Set[PIIType]] = None,
        replacement_char: str = "*",
        log_detections: bool = True,
    ) -> str:
        """
        Mask PII in text.
        
        Args:
            text: Text to mask
            masking_level: Level of masking to apply
            pii_types: Optional set of PII types to mask (masks all types if None)
            replacement_char: Character to use for masking
            log_detections: Whether to log detected PII (with values masked)
            
        Returns:
            Text with PII masked
        """
        # Detect PII
        detections = self.detect_pii(text, pii_types)
        
        if not detections:
            return text
            
        # Log detections if requested
        if log_detections and detections:
            masked_detections = []
            for detection in detections:
                # Create a copy with the value masked for logging
                masked_detection = detection.copy()
                masked_detection["value"] = self._mask_value(
                    masked_detection["value"], PIIMaskingLevel.PARTIAL, replacement_char
                )
                masked_detections.append(masked_detection)
                
            logger.info(
                f"Detected {len(detections)} PII items",
                extra={"masked_detections": masked_detections}
            )
            
        # Mask PII from end to start to preserve indices
        masked_text = text
        for detection in sorted(detections, key=lambda x: x["start"], reverse=True):
            start, end = detection["start"], detection["end"]
            original = text[start:end]
            
            # Apply appropriate masking
            if masking_level == PIIMaskingLevel.NONE:
                masked = original
            elif masking_level == PIIMaskingLevel.PARTIAL:
                masked = self._mask_value(original, PIIMaskingLevel.PARTIAL, replacement_char)
            elif masking_level == PIIMaskingLevel.FULL:
                masked = replacement_char * (end - start)
            elif masking_level == PIIMaskingLevel.HASH:
                masked = self._get_hash(original)
            elif masking_level == PIIMaskingLevel.PSEUDONYMIZE:
                masked = self._get_pseudonym(original, detection["type"])
            else:
                masked = replacement_char * (end - start)
                
            # Replace in text
            masked_text = masked_text[:start] + masked + masked_text[end:]
            
        return masked_text

    def _mask_value(self, value: str, level: PIIMaskingLevel, replacement_char: str) -> str:
        """
        Apply partial masking to a value.
        
        Args:
            value: Value to mask
            level: Masking level
            replacement_char: Character to use for masking
            
        Returns:
            Masked value
        """
        if level == PIIMaskingLevel.PARTIAL:
            # Special handling for different PII types
            if '@' in value:  # Email
                username, domain = value.split('@', 1)
                if len(username) > 2:
                    return username[0] + replacement_char * (len(username) - 2) + username[-1] + '@' + domain
                else:
                    return username[0] + replacement_char * (len(username) - 1) + '@' + domain
            elif len(value) > 4 and value.replace('-', '').replace(' ', '').isdigit():  # Card/phone
                # Keep last 4 digits
                digits = value.replace('-', '').replace(' ', '')
                visible = digits[-4:]
                return replacement_char * (len(digits) - 4) + visible
            elif len(value) > 2:
                # General case: keep first and last character
                return value[0] + replacement_char * (len(value) - 2) + value[-1]
            else:
                return replacement_char * len(value)
        else:
            return replacement_char * len(value)

    def _get_hash(self, value: str) -> str:
        """
        Generate a hash for a value.
        
        Args:
            value: Value to hash
            
        Returns:
            Hashed value
        """
        import hashlib
        return hashlib.sha256(value.encode()).hexdigest()[:10]

    def _get_pseudonym(self, value: str, pii_type: str) -> str:
        """
        Get a consistent pseudonym for a value.
        
        Args:
            value: Original value
            pii_type: Type of PII
            
        Returns:
            Pseudonym
        """
        # Create a key from the value and type
        key = f"{value}:{pii_type}"
        
        # Return existing pseudonym if we've seen this value before
        if key in self.pseudonym_map:
            return self.pseudonym_map[key]
            
        # Create a new pseudonym based on the PII type
        if pii_type == PIIType.EMAIL:
            import uuid
            username = f"user_{len(self.pseudonym_map) + 1}"
            domain = "example.com"
            pseudonym = f"{username}@{domain}"
        elif pii_type == PIIType.PHONE:
            pseudonym = f"555-{len(self.pseudonym_map) + 1:04d}"
        elif pii_type == PIIType.NAME:
            first_names = ["Alex", "Sam", "Jordan", "Taylor", "Casey"]
            last_names = ["Smith", "Jones", "Johnson", "Brown", "Miller"]
            import random
            pseudonym = f"{random.choice(first_names)} {random.choice(last_names)}"
        else:
            # Generic pseudonym for other types
            pseudonym = f"PSEUDO_{pii_type}_{len(self.pseudonym_map) + 1}"
            
        # Store for consistency
        self.pseudonym_map[key] = pseudonym
        return pseudonym
        
    def mask_pii_in_object(
        self,
        obj: Any,
        masking_level: PIIMaskingLevel = PIIMaskingLevel.FULL,
        pii_types: Optional[Set[PIIType]] = None,
        replacement_char: str = "*",
        log_detections: bool = True,
    ) -> Any:
        """
        Recursively mask PII in an object (dict, list, or string).
        
        Args:
            obj: Object to mask PII in
            masking_level: Level of masking to apply
            pii_types: Optional set of PII types to mask
            replacement_char: Character to use for masking
            log_detections: Whether to log detected PII
            
        Returns:
            Object with PII masked
        """
        if isinstance(obj, str):
            return self.mask_pii(obj, masking_level, pii_types, replacement_char, log_detections)
        elif isinstance(obj, dict):
            return {k: self.mask_pii_in_object(v, masking_level, pii_types, replacement_char, log_detections) 
                   for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.mask_pii_in_object(item, masking_level, pii_types, replacement_char, log_detections) 
                   for item in obj]
        else:
            # Return other types unchanged
            return obj
            
    def add_custom_pattern(
        self,
        regex: Union[str, Pattern],
        validation_func: Optional[callable] = None,
        description: Optional[str] = None
    ) -> None:
        """
        Add a custom PII detection pattern.
        
        Args:
            regex: Regular expression for detecting the PII
            validation_func: Optional function for additional validation beyond regex
            description: Human-readable description of the pattern
        """
        pattern = PIIPattern(
            PIIType.CUSTOM,
            regex,
            validation_func,
            description or "Custom PII pattern"
        )
        self.patterns.append(pattern)
        
    def get_safe_log_context(
        self,
        data: Dict[str, Any],
        sensitive_keys: Set[str] = None,
        masking_level: PIIMaskingLevel = PIIMaskingLevel.PARTIAL
    ) -> Dict[str, Any]:
        """
        Create a safe version of a data dictionary for logging.
        
        Args:
            data: Original data dictionary
            sensitive_keys: Set of known sensitive keys to mask
            masking_level: Level of masking to apply
            
        Returns:
            Safe version of the data for logging
        """
        # Default sensitive keys if none provided
        if sensitive_keys is None:
            sensitive_keys = {
                "password", "secret", "token", "key", "auth", "credential", "ssn", 
                "credit_card", "card_number", "cvv", "social_security"
            }
            
        # Create a copy to avoid modifying the original
        safe_data = {}
        
        for key, value in data.items():
            # Check if this is a sensitive key
            key_lower = key.lower()
            is_sensitive = any(sensitive_word in key_lower for sensitive_word in sensitive_keys)
            
            if is_sensitive:
                # Mask sensitive values completely
                if isinstance(value, str):
                    safe_data[key] = "[REDACTED]"
                elif isinstance(value, (list, dict)):
                    safe_data[key] = "[REDACTED COMPLEX VALUE]"
                else:
                    safe_data[key] = "[REDACTED]"
            elif isinstance(value, str):
                # Scan and mask PII in string values
                safe_data[key] = self.mask_pii(value, masking_level)
            elif isinstance(value, dict):
                # Recursively process nested dictionaries
                safe_data[key] = self.get_safe_log_context(value, sensitive_keys, masking_level)
            elif isinstance(value, list):
                # Process lists
                if all(isinstance(item, dict) for item in value):
                    # List of dictionaries
                    safe_data[key] = [
                        self.get_safe_log_context(item, sensitive_keys, masking_level)
                        for item in value
                    ]
                elif all(isinstance(item, str) for item in value):
                    # List of strings
                    safe_data[key] = [
                        self.mask_pii(item, masking_level)
                        for item in value
                    ]
                else:
                    # Mixed or primitive list
                    safe_data[key] = value
            else:
                # Pass through non-string, non-container values
                safe_data[key] = value
                
        return safe_data


# Create default instance for easy access
default_pii_masker = PIIMasker()
