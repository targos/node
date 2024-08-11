export interface DebugBinding {
  getV8FastApiCallCount(name: string): number;
  isEven(value: number): boolean;
  isOdd(value: number): boolean;
}
