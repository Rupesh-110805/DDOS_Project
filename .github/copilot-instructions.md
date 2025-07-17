<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# DDoS Detection System - Copilot Instructions

This is a Python-based DDoS detection system that uses Shannon entropy computing to detect Distributed Denial of Service attacks.

## Project Context
- **Purpose**: Educational/research project for DDoS detection using entropy analysis
- **Main Algorithm**: Shannon entropy calculation to identify attack patterns
- **Tech Stack**: Python backend, Flask web interface, real-time visualization
- **Key Components**: Entropy detector, packet simulator, web dashboard

## Code Guidelines
1. **Entropy Calculations**: Use Shannon entropy formula H(X) = -Σ p(x) * log2(p(x))
2. **Detection Logic**: Low entropy + high packet rate indicates potential DDoS
3. **Accuracy Metrics**: Calculate based on entropy confidence and packet distribution
4. **Real-time Processing**: Use deque for sliding window analysis
5. **Web Interface**: Flask with Socket.IO for real-time updates

## Key Files
- `entropy_detector.py`: Core detection algorithm with Shannon entropy
- `packet_simulator.py`: Traffic generation for testing (normal vs DDoS)
- `app.py`: Flask web application with real-time dashboard
- `main.py`: Command-line interface and demo runner
- `templates/index.html`: Web dashboard interface
- `static/app.js`: Frontend JavaScript for real-time visualization

## Performance Targets
- **Accuracy**: >90% detection rate for DDoS attacks
- **False Positives**: <5% for normal traffic
- **Response Time**: Real-time detection within 1-2 seconds
- **Throughput**: Handle 1000+ packets per second

## Security Considerations
- This is for educational purposes only
- Do not use for actual network attacks
- Implement proper rate limiting in production
- Consider legal implications of traffic simulation

When suggesting improvements:
- Focus on entropy calculation optimizations
- Suggest adaptive threshold mechanisms
- Recommend additional statistical features
- Consider machine learning enhancements for accuracy
