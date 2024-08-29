import re

from typing import Callable, Dict, Optional, List

from guardrails.validator_base import (
    ErrorSpan,
    FailResult,
    PassResult,
    ValidationResult,
    Validator,
    register_validator,
)

@register_validator(name="guardrails/internal_domains", data_type="string")
class InternalDomains(Validator):
    """# Overview

    | Developed by | David Tam |
    | Date of development | Aug 13, 2024 |
    | Validator type | Format |
    | License | Apache 2 |
    | Input/Output | Output |

    # Description
    Identifies internal domains in a string output.
    
    ## (Optional) Intended Use
    finds internal domains in a string output like "internal.example.com" or "example.internal".

    ## Requirements

    * Dependencies:
        - guardrails-ai>=0.4.0

    * Dev Dependencies:
        - pytest
        - pyright
        - ruff

    # Installation

    ```bash
    $ guardrails hub install hub://guardrails/internal_domains
    ```

    # Usage Examples

    ## Validating string output via Python

    In this example, we apply the validator to a string output generated by an LLM.

    ```python
    # Import Guard and Validator
    from guardrails.hub import InternalDomains
    from guardrails import Guard

    # Setup Guard
    guard = Guard.use(
        InternalDomains(internal_domains= ["internal.example.com"]),
    )

    guard.validate("This is a string with no domains except a reference to https://www.example.com")  # Validator passes
    guard.validate("This string includes a link to https://internal.example.com/wiki/welcome-guide")  # Validator fails
    ```
    """  # noqa
    def __init__(self, internal_domains: List[str], on_fail: Optional[Callable] = None):
        super().__init__(on_fail=on_fail, internal_domains=internal_domains)
        self.internal_domains = internal_domains

    def _validate(self, value: str, metadata: Dict) -> ValidationResult:
        mentioned_domains = []
        error_spans = []

        # find uris in value
        # Regex pattern to match URIs for the specified domain or domain alone
        for domain in self.internal_domains:
            pattern = rf"https?://(?:\w+\.)*{re.escape(domain)}(?:/[\w\-/]*)?|{re.escape(domain)}(?:/[\w\-/]*)?"
            # Find all matches
             # Find all matches
            for match in re.finditer(pattern, value):
                mentioned_domains.append(match.group())
                span_start = match.start()
                span_end = match.end()
                error_spans.append(ErrorSpan(
                    start=span_start, 
                    end=span_end, 
                    reason=f"Internal domain detected in {span_start}:{span_end}",))

        if len(mentioned_domains) > 0:
            on_fix = value
            for domain in mentioned_domains:
                # Filter out the mentioned_domains
                on_fix = on_fix.replace(domain, f"{'*' * len(domain)}")
            return FailResult(
                error_message=f"Found internal domains: {', '.join(mentioned_domains)}",
                fix_value=on_fix,
                error_spans=error_spans,
            )
        else:
            return PassResult()


