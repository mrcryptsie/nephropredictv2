import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { PredictionInput, predictionInputSchema } from "@shared/schema";
import { makeRequestToFastAPI } from "./prediction";
import { ContactFormData } from "@shared/types";
import { z } from "zod";

const contactFormSchema = z.object({
  name: z.string().min(2),
  email: z.string().email(),
  subject: z.string().min(1),
  message: z.string().min(10),
});

export async function registerRoutes(app: Express): Promise<Server> {
  // Prediction API endpoint
  app.post("/predict", async (req, res) => {
    try {
      // Validate input data
      const parsedData = predictionInputSchema.safeParse(req.body);
      
      if (!parsedData.success) {
        return res.status(400).json({ 
          message: "Invalid input data", 
          errors: parsedData.error.format() 
        });
      }
      
      const predictionInput: PredictionInput = parsedData.data;
      
      // Call FastAPI prediction service
      const predictionResult = await makeRequestToFastAPI(predictionInput);
      
      // Return prediction results
      return res.status(200).json(predictionResult);
    } catch (error) {
      console.error("Prediction error:", error);
      return res.status(500).json({ 
        message: "An error occurred during prediction", 
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });
  
  // Contact form endpoint
  app.post("/contact", async (req, res) => {
    try {
      // Validate input data
      const parsedData = contactFormSchema.safeParse(req.body);
      
      if (!parsedData.success) {
        return res.status(400).json({ 
          message: "Invalid form data", 
          errors: parsedData.error.format() 
        });
      }
      
      const contactData: ContactFormData = parsedData.data;
      
      // Here we'd typically send an email or store the contact form data
      // For now, we'll just log it and return success
      console.log("Contact form submission:", contactData);
      
      return res.status(200).json({ 
        message: "Contact form submitted successfully" 
      });
    } catch (error) {
      console.error("Contact form error:", error);
      return res.status(500).json({ 
        message: "An error occurred while processing your request", 
        error: error instanceof Error ? error.message : String(error)
      });
    }
  });

  const httpServer = createServer(app);
  
  return httpServer;
}
