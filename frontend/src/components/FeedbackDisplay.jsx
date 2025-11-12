/**
 * FeedbackDisplay Component

 */

const FeedbackDisplay = ({ feedback, onClose }) => {
  if (!feedback) return null;
  
  const parseFeedback = (feedbackText) => {
    // If feedback is already an object with structured data
    if (typeof feedback === 'object' && feedback.metadata?.feedback) {
      return feedback.metadata.feedback;
    }
    
    // Otherwise parse the text
    return {
      overall_assessment: 'Thank you for completing the interview!',
      strengths: [],
      areas_for_improvement: [],
      specific_suggestions: [],
      encouragement: feedbackText
    };
  };
  
  const feedbackData = parseFeedback(feedback);
  
  return (
    <div style={styles.overlay}>
      <div style={styles.modal}>
        <div style={styles.header}>
          <h2 style={styles.title}>Interview Feedback</h2>
          <button onClick={onClose} style={styles.closeButton}>✕</button>
        </div>
        
        <div style={styles.content}>
          {/* Overall Assessment */}
          {feedbackData.overall_assessment && (
            <section style={styles.section}>
              <h3 style={styles.sectionTitle}> Overall Assessment</h3>
              <p style={styles.text}>{feedbackData.overall_assessment}</p>
            </section>
          )}
          
          {/* Strengths */}
          {feedbackData.strengths && feedbackData.strengths.length > 0 && (
            <section style={styles.section}>
              <h3 style={styles.sectionTitle}>Your Strengths</h3>
              <ul style={styles.list}>
                {feedbackData.strengths.map((strength, idx) => (
                  <li key={idx} style={styles.listItem}>{strength}</li>
                ))}
              </ul>
            </section>
          )}
          
          {/* Areas for Improvement */}
          {feedbackData.areas_for_improvement && feedbackData.areas_for_improvement.length > 0 && (
            <section style={styles.section}>
              <h3 style={styles.sectionTitle}>Areas for Improvement</h3>
              <ul style={styles.list}>
                {feedbackData.areas_for_improvement.map((area, idx) => (
                  <li key={idx} style={styles.listItem}>{area}</li>
                ))}
              </ul>
            </section>
          )}
          
          {/* Specific Suggestions */}
          {feedbackData.specific_suggestions && feedbackData.specific_suggestions.length > 0 && (
            <section style={styles.section}>
              <h3 style={styles.sectionTitle}> Specific Suggestions</h3>
              <ul style={styles.list}>
                {feedbackData.specific_suggestions.map((suggestion, idx) => (
                  <li key={idx} style={styles.listItem}>{suggestion}</li>
                ))}
              </ul>
            </section>
          )}
          
          {/* Encouragement */}
          {feedbackData.encouragement && (
            <section style={{...styles.section, ...styles.encouragementSection}}>
              <h3 style={styles.sectionTitle}>Words of Encouragement</h3>
              <p style={styles.encouragementText}>{feedbackData.encouragement}</p>
            </section>
          )}
          
          {/* If feedback is just text */}
          {typeof feedback === 'string' && (
            <section style={styles.section}>
              <pre style={styles.feedbackText}>{feedback}</pre>
            </section>
          )}
        </div>
        
        <div style={styles.footer}>
          <button onClick={onClose} style={styles.primaryButton}>
            Close Feedback
          </button>
        </div>
      </div>
    </div>
  );
};

const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(0, 0, 0, 0.7)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 1000,
    padding: '20px',
  },
  modal: {
    background: 'white',
    borderRadius: '20px',
    maxWidth: '800px',
    width: '100%',
    maxHeight: '90vh',
    display: 'flex',
    flexDirection: 'column',
    boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '25px 30px',
    borderBottom: '1px solid #e0e0e0',
  },
  title: {
    margin: 0,
    fontSize: '28px',
    color: '#333',
  },
  closeButton: {
    background: 'none',
    border: 'none',
    fontSize: '28px',
    cursor: 'pointer',
    color: '#999',
    padding: '0',
    width: '30px',
    height: '30px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  content: {
    flex: 1,
    overflowY: 'auto',
    padding: '30px',
  },
  section: {
    marginBottom: '30px',
  },
  sectionTitle: {
    fontSize: '20px',
    marginBottom: '15px',
    color: '#667eea',
    fontWeight: '600',
  },
  text: {
    fontSize: '16px',
    lineHeight: '1.6',
    color: '#555',
  },
  list: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
  },
  listItem: {
    fontSize: '16px',
    lineHeight: '1.6',
    color: '#555',
    marginBottom: '10px',
    paddingLeft: '25px',
    position: 'relative',
  },
  encouragementSection: {
    background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)',
    padding: '20px',
    borderRadius: '15px',
  },
  encouragementText: {
    fontSize: '18px',
    lineHeight: '1.8',
    color: '#333',
    fontWeight: '500',
  },
  feedbackText: {
    whiteSpace: 'pre-wrap',
    fontSize: '14px',
    lineHeight: '1.6',
    color: '#555',
    fontFamily: 'inherit',
  },
  footer: {
    padding: '20px 30px',
    borderTop: '1px solid #e0e0e0',
    display: 'flex',
    justifyContent: 'center',
  },
  primaryButton: {
    padding: '12px 40px',
    fontSize: '16px',
    borderRadius: '50px',
    border: 'none',
    cursor: 'pointer',
    fontWeight: '600',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
  },
};

// Add list item bullets via CSS
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = `
    li[style*="position: relative"]::before {
      content: "✓";
      position: absolute;
      left: 0;
      color: #667eea;
      font-weight: bold;
    }
  `;
  document.head.appendChild(styleSheet);
}

export default FeedbackDisplay;

