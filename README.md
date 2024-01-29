# GPTRA

## Overview
The Academic Helper App is a Streamlit-based application to assist in various academic tasks, including paper writing, email composition, programming, and more. It leverages OpenAI's GPT models to generate responses based on user inputs. It is basically just an easy way to craft prompts for often repeated tasks. 

## Features
- **Reviewer Response Generator**: Helps in crafting responses to reviewer comments for journal publications.
- **Paper Writing Assistant**: Assists in developing content for academic papers.
- **Email Composition**: Aids in writing concise and polite emails.
- **Programming Support**: Provides assistance in various programming languages.
- **Chat Interface**: A chatbot for general queries and assistance.
- **Custom Prompt Generator**: Allows users to create custom prompts for specific needs.

Remember to change the various system prompts to suit your needs. 

## Installation
1. Clone the repository:
   ```
   git clone https://github.com/murtaza-nasir/gptra.git
   ```
2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

## Configuration
1. **OpenAI API Key**: Add your OpenAI API key to the Streamlit secrets file. This key is crucial for the app to communicate with OpenAI's models.

2. **Local Models**: If using local models, modify or remove the lines pertaining to the local model endpoints in the code.

## Usage
To run the app, navigate to the app directory and execute:
```
streamlit run app.py
```

## License
This project is licensed under the AGPL-3.0 license.

## Citation
If you use this application in your research or work, please cite it as follows:
- **APA**: Nasir, M. (2024). Academic Helper App. Retrieved from [https://murtaza.cc](https://murtaza.cc)
- **MLA**: Nasir, Murtaza. "Academic Helper App". 2024, [https://murtaza.cc](https://murtaza.cc).
- **Chicago**: Nasir, Murtaza. 2024. "Academic Helper App". [https://murtaza.cc](https://murtaza.cc).

For any further inquiries or contributions, please visit [Dr. Murtaza Nasir's website](https://murtaza.cc).

## Contributions
We welcome contributions from the community. Please submit a pull request or open an issue to propose changes or additions.

## Contact
- **Author**: Dr. Murtaza Nasir
- **Website**: [https://murtaza.cc](https://murtaza.cc)

## Acknowledgements
Special thanks to OpenAI for providing the GPT models that power this application.
