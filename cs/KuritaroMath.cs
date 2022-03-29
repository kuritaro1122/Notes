public static class KuritaroMath {
  public static float Mod(float left, float right) {
    float add = right * (int)(left / right + 1) * -1;
      left = Mathf.Max(left, 0f);
      add = Mathf.Max(add, 0f);
      return (left + add) % right;
  }
}
