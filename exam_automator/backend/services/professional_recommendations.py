"""
Professional Plagiarism Recommendations Generator
Replaces emoji-heavy recommendations with clean, actionable feedback
"""

def generate_professional_recommendations(originality_score: float,
                                         ai_generated_count: int,
                                         ai_high_confidence: int,
                                         internal_copies_count: int,
                                         internal_high_similarity: int,
                                         exact_matches_count: int,
                                         paraphrased_count: int,
                                         submission_type: str) -> list[str]:
    """
    Generate professional, emoji-free recommendations
    
    Returns:
        List of formatted recommendation strings
    """
    recommendations = []
    
    # Overall Risk Assessment
    if originality_score >= 90:
        recommendations.append("**ASSESSMENT: EXCELLENT ORIGINALITY** - Content demonstrates strong original work with minimal integrity concerns.")
    elif originality_score >= 70:
        recommendations.append("**ASSESSMENT: MINOR CONCERNS** - Some similarities detected that warrant further review.")
    elif originality_score >= 50:
        recommendations.append("**ASSESSMENT: MODERATE RISK** - Significant similarities found. Manual review and student interview required.")
    else:
        recommendations.append("**ASSESSMENT: HIGH RISK** - Substantial plagiarism indicators detected. Immediate investigation recommended.")
    
    # AI-Generated Code Analysis
    if ai_generated_count > 0:
        if ai_high_confidence > 0:
            recommendations.append(
                f"\n**AI-GENERATED CONTENT DETECTED** ({ai_high_confidence} high-confidence detection{'s' if ai_high_confidence > 1 else ''}):"
            )
            recommendations.append("  • Evidence includes: Over-commenting, perfect formatting, generic naming patterns")
            recommendations.append("\n  REQUIRED ACTIONS:")
            recommendations.append("  1. Schedule meeting with student to discuss findings")
            recommendations.append("  2. Request original drafts, notes, or development history")
            recommendations.append("  3. Ask student to explain key concepts/code sections")
            recommendations.append("  4. Consider re-submission opportunity with proper citations")
            recommendations.append("  5. Document findings and meeting outcomes for records")
        else:
            recommendations.append(
                f"\n**POSSIBLE AI ASSISTANCE** ({ai_generated_count} low-confidence detection{'s' if ai_generated_count > 1 else ''}):"
            )
            recommendations.append("  • Some AI patterns detected but not conclusive")
            recommendations.append("  • May indicate use of AI autocomplete or code suggestions")
            recommendations.append("\n  RECOMMENDED ACTIONS:")
            recommendations.append("  1. Review institution's AI tool usage policy with student")
            recommendations.append("  2. Clarify acceptable vs. unacceptable AI assistance")
            recommendations.append("  3. Document discussion for future reference")
    
    # Internal Plagiarism Analysis
    if internal_copies_count > 0:
        if internal_high_similarity > 0:
            recommendations.append(
                f"\n**INTERNAL FILE DUPLICATION** ({internal_high_similarity} high-similarity match{'es' if internal_high_similarity > 1 else ''}):"
            )
            recommendations.append("  • Files contain nearly identical code blocks")
            recommendations.append("  • This may indicate: Copy-paste programming, code generation, or misuse of templates")
            recommendations.append("\n  REQUIRED ACTIONS:")
            recommendations.append("  1. Verify student can explain code purpose and implementation differences")
            recommendations.append("  2. Check if proper refactoring techniques were applied (functions/modules vs. duplication)")
            recommendations.append("  3. Review assignment requirements regarding code reuse")
        else:
            recommendations.append(
                f"\n**CODE SIMILARITY DETECTED** ({internal_copies_count} moderate match{'es' if internal_copies_count > 1 else ''}):"
            )
            recommendations.append("  • Some code blocks share similar structure")
            recommendations.append("  • Could indicate legitimate shared utilities or assignment templates")
            recommendations.append("\n  RECOMMENDED ACTIONS:")
            recommendations.append("  1. Review if code reuse is appropriate for this assignment")
            recommendations.append("  2. Verify student understanding of shared code sections")
    
    # Exact Matches
    if exact_matches_count > 0:
        recommendations.append(
            f"\n**EXACT/NEAR-EXACT MATCHES FOUND** ({exact_matches_count} instance{'s' if exact_matches_count > 1 else ''}):"
        )
        recommendations.append("  • Verbatim or nearly verbatim content detected from external sources")
        recommendations.append("\n  REQUIRED ACTIONS:")
        recommendations.append("  1. Verify if content includes proper quotations and citations")
        recommendations.append("  2. Check if matched content is allowed reference material")
        recommendations.append("  3. Review institution's citation and attribution policies")
        recommendations.append("  4. Consider academic integrity violation if improperly cited")
    
    # Paraphrased Content
    if paraphrased_count > 0:
        recommendations.append(
            f"\n**PARAPHRASING PATTERNS DETECTED** ({paraphrased_count} instance{'s' if paraphrased_count > 1 else ''}):"
        )
        recommendations.append("  • Content shows structural similarity to external sources")
        recommendations.append("  • May indicate superficial rewording without proper attribution")
        recommendations.append("\n  REQUIRED ACTIONS:")
        recommendations.append("  1. Ensure proper attribution of ideas and concepts")
        recommendations.append("  2. Verify paraphrasing is substantial, not just synonym substitution")
        recommendations.append("  3. Check that student's own analysis and interpretation is present")
    
    # Type-specific best practices
    if submission_type == "code":
        recommendations.append(
            "\n**CODE SUBMISSION BEST PRACTICES:**"
        )
        recommendations.append("  • Similar algorithms are acceptable if independently implemented")
        recommendations.append("  • Code should demonstrate understanding through meaningful comments and variable names")
        recommendations.append("  • Avoid copying implementation details from online sources (Stack Overflow, GitHub, etc.)")
        recommendations.append("  • Document any external libraries, frameworks, or code snippets used")
        recommendations.append("  • Include comments explaining your problem-solving approach")
    else:
        recommendations.append(
            "\n**WRITTEN WORK BEST PRACTICES:**"
        )
        recommendations.append("  • Use quotation marks for all direct quotes")
        recommendations.append("  • Cite all sources following required format (APA, MLA, Chicago, etc.)")
        recommendations.append("  • Paraphrase substantially - don't just rearrange words or use synonyms")
        recommendations.append("  • Include proper bibliography/references section")
        recommendations.append("  • Ensure your own analysis and interpretation is clearly present")
    
    return recommendations


# Example usage for testing
if __name__ == "__main__":
    recs = generate_professional_recommendations(
        originality_score=65.0,
        ai_generated_count=2,
        ai_high_confidence=1,
        internal_copies_count=3,
        internal_high_similarity=2,
        exact_matches_count=0,
        paraphrased_count=0,
        submission_type="code"
    )
    
    print("="*80)
    print("PROFESSIONAL RECOMMENDATIONS")
    print("="*80)
    for rec in recs:
        print(rec)
    print("="*80)
