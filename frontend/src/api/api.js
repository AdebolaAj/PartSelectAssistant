import OpenAI from "openai";

const apiKey = process.env.REACT_APP_DEEPSEEK_API_KEY;

const openai = new OpenAI({
  baseURL: 'https://api.deepseek.com',
  apiKey: apiKey,
  dangerouslyAllowBrowser: true
});

const systemMessage = {
  role: "system",
  content: `You are a chatbot agent for the PartSelect website. Use the retrieved context to answer as a chatbot to a user.
  Do not add "Based on the retrieved context," in your response. The font size
  should be the same for the entire text response.
  If a part is not in the list of compatible parts for a model then they are not compatible.
  If installation instructions in the retrieved context are "n/a", "N/A", or otherwise unavailable,
  tell the user: "Installation instructions are not available on PartSelect at the moment."
  If you are not sure about file content or codebase structure pertaining to
  the user's request, use your tools to read files and gather the relevant
  information: do NOT guess or make up an answer.
  If retrieved context does not provide adequate information to answer the user question,
  then respond saying I currently do not have information regarding this product. Please try again later.`
};

export const getAIMessage = async (userQuery, oldMessages) => {
  try {
    // error returns for checking in scope
    const inscope = await checkInScope(userQuery);
    if (inscope === "None") {
      return {
        role: "assistant",
        content: `Sorry that's outside of what I can assist with, but I'm happy to help with other questions related to PartSelect products!`
      };
    } else if (inscope === "Error") {
      return {
        role: "assistant",
        content: `Sorry, there was an error processing your request. Please try again later`
      };
    }

    // error catching for context
    const retrievedContext = await getContext(userQuery);
    if (retrievedContext === "Error") {
      return {
        role: "assistant",
        content: `Sorry, there was an error processing your request. Please try again later`
      };
    }

    let newMessages;
    if (oldMessages.length === 1) {
      newMessages = [
        systemMessage,
        {
          "role": "user",
          "content": `Context: ${retrievedContext}\n\nQuestion: ${userQuery}`
        }
      ];
    } else {
      newMessages = [
        systemMessage,
        ...oldMessages,
        {
          "role": "user",
          "content": `Context: ${retrievedContext}\n\nQuestion: ${userQuery}`
        }
      ];
    }

    const response = await openai.chat.completions.create({
      model: "deepseek-chat",
      messages: newMessages
    });

    const textResponse = response.choices[0].message.content;

    const message = {
      role: "assistant",
      content: textResponse
    };

    return message;
  } catch (error) {
    console.error("Error in getAIMessage:", error);
    return {
      role: "assistant",
      content: "Sorry, there was an error processing your request. Please try again later."
    };
  }
};

export const checkInScope = async (userQuery) => {
  try {
    const response = await openai.chat.completions.create({
      model: "deepseek-chat",
      messages: [
        {
          "role": "system",
          "content": `You are an agent that determines if 
            the given query is in or out of scope. 
            If the query is not a question about PartSelect product information or assistance with
            installation or a PartSelect product, return None. If the question is in scope then return Pass. Your
            response is limited to a single string: either "None" or "Pass"`
        },
        {
          "role": "user",
          "content": userQuery
        }
      ]
    });

    const textResponse = response.choices[0].message.content;
    return textResponse;
  } catch (error) {
    console.error("Error in checkInScope:", error);
    return "Error";
  }
};

export const getContext = async (userQuery) => {
  try {
    const res = await fetch("http://localhost:8001/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: userQuery })
    });

    if (!res.ok) {
      throw new Error(`HTTP error! Status: ${res.status}`);
    }

    const data = await res.json();
    console.log(data)
    return data.results['documents'][0].toString();
  } catch (error) {
    console.error("Error in getContext:", error);
    return "Error";
  }
};
